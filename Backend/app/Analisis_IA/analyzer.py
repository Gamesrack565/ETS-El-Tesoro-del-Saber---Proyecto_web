# Version: 3.0
# Archivo: Analisis_IA/analyzer.py
# Descripción: Módulo para analizar reseñas de profesores usando Google Gemini.

import json
import os
import re
import time
from typing import List, Dict, Any
import google.generativeai as genai
from google.api_core import exceptions
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()


class KeyManager:
    """
    Gestor de claves de API para Google Gemini.

    Permite la rotación automática de claves cuando se agota la cuota
    de una de ellas.
    """

    def __init__(self):
        """
        Inicializa el gestor cargando las claves desde variables de entorno.

        Busca GEMINI_API_KEY_1, _2, _3, o una clave única GEMINI_API_KEY.
        Raises:
            ValueError: Si no se encuentran claves configuradas.
        """
        self.keys = [
            os.getenv("GEMINI_API_KEY_1"),
            os.getenv("GEMINI_API_KEY_2"),
            os.getenv("GEMINI_API_KEY_3")
        ]
        # Filtrar claves vacías o None
        self.keys = [k for k in self.keys if k]

        if not self.keys:
            if os.getenv("GEMINI_API_KEY"):
                self.keys = [os.getenv("GEMINI_API_KEY")]
            else:
                raise ValueError("No hay API Keys configuradas.")

        self.current_index = 0

    def get_current_key(self) -> str:
        """Devuelve la clave API actual."""
        return self.keys[self.current_index]

    def switch_key(self) -> str:
        """
        Cambia a la siguiente clave API disponible de forma circular.

        Returns:
            str: La nueva clave API activa.
        """
        prev = self.current_index
        self.current_index = (self.current_index + 1) % len(self.keys)
        print(f"Rotando API Key: {prev + 1} -> {self.current_index + 1}")
        return self.get_current_key()


# Inicialización global del gestor de claves
key_manager = KeyManager()
genai.configure(api_key=key_manager.get_current_key())

# --- CONFIGURACIÓN OPTIMIZADA ---
# Tamaño del lote para procesamiento. 100 equilibra velocidad y contexto.
BATCH_SIZE = 100

AVAILABLE_MODELS = [
    'gemini-2.5-flash-lite',
    'gemini-2.5-flash'
]

# Configuración de Seguridad: PERMITIR TODO
# Se desactivan los filtros de seguridad ya que el input (reseñas)
# puede contener lenguaje coloquial u ofensivo que debe ser procesado.
SAFETY_SETTINGS = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]


def analyze_batch_with_retry(
    messages_batch: List[Dict[str, Any]],
    max_retries: int = 5
) -> List[Dict[str, Any]]:
    """
    Envía un lote de mensajes a la API de Gemini con lógica de reintento.

    Maneja la rotación de modelos y claves API en caso de fallos o cuotas.

    Args:
        messages_batch (List[Dict]): Lista de mensajes a analizar.
        max_retries (int): Número máximo de intentos antes de desistir.

    Returns:
        List[Dict]: Lista de objetos JSON limpios con la información extraída.
    """
    # Construcción del input simplificado para el modelo
    chat_lines = [
        f"[{m['id']}] {m['author']}: {m['message']}" for m in messages_batch
    ]
    chat_text = "\n".join(chat_lines)

    # Prompt con formato COMPRIMIDO para ahorrar tokens.
    # Se usan dobles llaves {{ }} para escapar el JSON en el f-string.
    prompt = f"""
    ANALISTA: Extrae reseñas de profesores. IGNORA preguntas.
    CHAT:
    ---
    {chat_text}
    ---

    REGLAS:
    1. SI NO HAY OPINIÓN CLARA O ES PREGUNTA: IGNORAR.
    2. FORMATO JSON COMPACTO (Ahorra tokens):
       "n": Nombre Profesor (Normalizado)
       "c": Comentario (Resumido)
       "s": Score/Calificación (1-10)
       "d": Dificultad (1-10)
       "id": ID del mensaje original

    EJEMPLO:
    [
      {{"n": "Lopez Juan", "c": "Es barco", "s": 10, "d": 1, "id": 45}}
    ]
    """

    model_index = 0

    for attempt in range(max_retries):
        try:
            current_model_name = AVAILABLE_MODELS[model_index]
            current_model = genai.GenerativeModel(current_model_name)

            # Llamada a la API
            response = current_model.generate_content(
                prompt,
                generation_config={
                    "response_mime_type": "application/json",
                    "max_output_tokens": 8192,
                    "temperature": 0.0
                },
                safety_settings=SAFETY_SETTINGS
            )

            # --- DIAGNÓSTICO DE CORTE ---
            # Verificar si la respuesta se cortó por límite de tokens
            if hasattr(response.candidates[0], 'finish_reason'):
                reason = response.candidates[0].finish_reason
                if reason == 2:  # MAX_TOKENS
                    # Excepción manual para activar la lógica de reintento
                    raise exceptions.ResourceExhausted("Corte por Max Tokens")

            raw_text = response.text
            # Limpieza básica de markdown
            clean_text = raw_text.replace("```json", "")
            clean_text = clean_text.replace("```", "").strip()

            # Regex para extraer estrictamente la lista JSON [...]
            match = re.search(r'\[.*\]', clean_text, re.DOTALL)
            if match:
                clean_text = match.group(0)

            if not clean_text or clean_text == "[]":
                return []

            data = json.loads(clean_text)

            # --- EL BARRENDERO Y DESCOMPRESOR ---
            # Normalización y filtrado de "alucinaciones" del modelo
            data_clean = []

            # Lista de palabras clave que indican falsos positivos
            nombres_prohibidos = [
                "PROFESOR", "AYDA", "BASE DE DATOS", "CALCULO", "ESIME",
                "ESCOM", "GOD", "DESCONOCIDO", "ALGUIEN", "REINAS"
            ]
            frases_basura = [
                "sin respuesta", "preguntado por", "nadie contestó",
                "no hay información", "se desconoce"
            ]

            for item in data:
                # Extracción segura con valores por defecto
                nombre = item.get('n', '').upper()
                comentario = item.get('c', '')
                calif = item.get('s')
                dificultad = item.get('d')
                autor_id = item.get('id')

                # Filtros de validación
                if calif is None or dificultad is None:
                    continue

                # Comprobar frases basura en comentario
                if any(f in comentario.lower() for f in frases_basura):
                    continue

                # Comprobar validez del nombre
                name_bad = any(b in nombre for b in nombres_prohibidos)
                if len(nombre) < 4 or name_bad:
                    continue

                # Construcción del objeto final normalizado
                obj_final = {
                    "profesor_nombre": item.get('n'),
                    "comentario": comentario,
                    "calificacion": calif,
                    "dificultad": dificultad,
                    "autor_original_id": autor_id
                }

                data_clean.append(obj_final)

            return data_clean

        except (exceptions.ResourceExhausted,
                exceptions.ServiceUnavailable) as e:
            err_msg = str(e)
            tipo_err = "CORTE" if "Corte" in err_msg else "CUOTA AGOTADA"

            print(f"Fallo en {AVAILABLE_MODELS[model_index]}: {tipo_err}")

            # Lógica de fallback: Cambiar modelo -> Fallan todos -> Rotar Key
            if model_index < len(AVAILABLE_MODELS) - 1:
                model_index += 1
                print(f"Cambiando a: {AVAILABLE_MODELS[model_index]}")
                time.sleep(1)
                continue
            else:
                print("Key agotada. ROTANDO API KEY...")
                new_key = key_manager.switch_key()
                genai.configure(api_key=new_key)
                model_index = 0  # Reiniciar modelo con nueva key
                time.sleep(2)
                continue

        except json.JSONDecodeError:
            print("Error JSON. Reintentando...")
            time.sleep(1)
            continue

        except Exception as e:
            print(f"Error General: {e}")
            time.sleep(1)
            continue

    return []


def analyze_reviews(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Función principal que orquesta el análisis de una lista de mensajes.

    Divide los mensajes en lotes, procesa cada lote y reasocia los IDs
    con los nombres de los autores originales.

    Args:
        messages (List[Dict]): Lista completa de mensajes crudos.

    Returns:
        List[Dict]: Lista consolidada de todas las reseñas extraídas.
    """
    clean_messages = []

    # Preprocesamiento: asignar IDs temporales y filtrar mensajes muy cortos
    for i, msg in enumerate(messages):
        if len(msg['message']) > 10:
            msg_with_id = msg.copy()
            msg_with_id['id'] = i
            clean_messages.append(msg_with_id)

    all_reviews = []
    total_messages = len(clean_messages)

    print(f"--- Iniciando analisis de {total_messages} mensajes ---")
    print(f"--- Modelo Base: {AVAILABLE_MODELS[0]} | Lote: {BATCH_SIZE} ---")

    # Procesamiento por lotes
    for i in range(0, total_messages, BATCH_SIZE):
        batch = clean_messages[i:i + BATCH_SIZE]
        print(f"Procesando lote {i} a {i + len(batch)}...")

        batch_reviews = analyze_batch_with_retry(batch)

        # Post-procesamiento: Recuperar el nombre del autor original
        for review in batch_reviews:
            raw_id = review.get("autor_original_id", -1)
            found_author = "Desconocido"

            try:
                msg_id = int(str(raw_id))
                # Búsqueda eficiente del mensaje original por ID
                original_msg = next(
                    (m for m in clean_messages if m['id'] == msg_id), None
                )
                if original_msg:
                    found_author = original_msg["author"]
            except ValueError:
                found_author = str(raw_id)

            review["autor_original"] = found_author

            # Limpieza final: eliminar el ID temporal interno
            if "autor_original_id" in review:
                del review["autor_original_id"]

            all_reviews.append(review)

    print(f"--- Analisis finalizado. Reseñas: {len(all_reviews)} ---")
    return all_reviews
