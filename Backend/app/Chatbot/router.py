import json
import os
import re
import time
from datetime import datetime, timedelta

import google.generativeai as genai
from dotenv import load_dotenv
from fastapi import APIRouter, Depends
from google.api_core import exceptions
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.Chatbot import esquemas
from app.Chatbot.modelos import HistorialChat
from app.Creacion_mats_prof import modelos as main_models
from app.database import get_db
from app.Porta_Estudio import modelos as study_models

load_dotenv()


# ==========================================
# CONFIGURACION Y GESTOR DE LLAVES
# ==========================================

class KeyManager:
    """
    Gestor de claves de API para Google Gemini.
    Administra la rotacion de multiples claves para evitar limites de cuota.
    """

    def __init__(self):
        """Inicializa el gestor cargando las llaves desde el entorno."""
        self.keys = [
            os.getenv("GEMINI_API_KEY_4"),
            os.getenv("GEMINI_API_KEY_5"),
            os.getenv("GEMINI_API_KEY_6")
        ]
        # Filtrar claves nulas o vacias
        self.keys = [k for k in self.keys if k]

        if not self.keys:
            single = os.getenv("GEMINI_API_KEY")
            if single:
                self.keys = [single]
            else:
                raise ValueError(
                    "Error Critico: No hay API Keys configuradas en .env"
                )
        self.current_index = 0

    def get_current_key(self):
        """Devuelve la llave de API activa actualmente."""
        return self.keys[self.current_index]

    def switch_key(self):
        """Cambia a la siguiente llave disponible en la lista (rotación)."""
        prev = self.current_index
        self.current_index = (self.current_index + 1) % len(self.keys)
        print(
            f"Chatbot: Rotando Key "
            f"({prev + 1} -> {self.current_index + 1})..."
        )
        return self.get_current_key()


key_manager = KeyManager()
genai.configure(api_key=key_manager.get_current_key())

AVAILABLE_MODELS = [
    'gemini-2.5-flash-lite',
    'gemini-2.5-flash'
]


# ==========================================
# GENERADOR INTELIGENTE (WRAPPER IA)
# ==========================================

def generate_smart(prompt: str, max_retries: int = 2) -> str:
    """
    Genera contenido usando Google Gemini con manejo de errores y rotacion
    de modelos y llaves de API.
    """
    model_index = 0
    total_attempts = max_retries * len(AVAILABLE_MODELS)

    for _ in range(total_attempts):
        try:
            current_model_name = AVAILABLE_MODELS[model_index]
            model = genai.GenerativeModel(current_model_name)
            response = model.generate_content(prompt)
            return response.text

        except (exceptions.ResourceExhausted,
                exceptions.ServiceUnavailable,
                exceptions.InternalServerError) as e:
            print(f"Fallo en {AVAILABLE_MODELS[model_index]}: {e}")

            # Intenta cambiar de modelo primero
            if model_index < len(AVAILABLE_MODELS) - 1:
                model_index += 1
                time.sleep(1)
                continue
            else:
                # Si fallan los modelos, rota la API Key
                new_key = key_manager.switch_key()
                genai.configure(api_key=new_key)
                model_index = 0
                time.sleep(2)
                continue

        except Exception:
            return (
                "Lo siento, tuve un error interno al "
                "procesar tu solicitud."
            )

    return "El sistema esta saturado en este momento."


# ==========================================
# LIMITADOR DE TASA (RATE LIMITING)
# ==========================================

LIMITE_PREGUNTAS = 150   # Maximo de preguntas permitidas
VENTANA_TIEMPO_HORAS = 2  # Ventana de tiempo en horas


def verificar_limite_usuario(user_id: int, db: Session) -> bool:
    """
    Verifica si el usuario ha excedido el límite de preguntas permitidas
    en una ventana de tiempo específica.
    """
    if not user_id:
        return True  # Invitados no tienen limite

    tiempo_limite = datetime.utcnow() - timedelta(hours=VENTANA_TIEMPO_HORAS)

    cantidad = db.query(HistorialChat).filter(
        HistorialChat.user_id == user_id,
        HistorialChat.role == "user",
        HistorialChat.timestamp >= tiempo_limite
    ).count()

    if cantidad >= LIMITE_PREGUNTAS:
        return False

    return True


# ==========================================
# FUNCIONES DE MEMORIA
# ==========================================

def recuperar_historial(user_id: int, db: Session, limite: int = 6) -> str:
    """
    Recupera los últimos mensajes de la conversación del usuario
    para mantener el contexto del chat.
    """
    if not user_id:
        return ""

    mensajes = db.query(HistorialChat).filter(
        HistorialChat.user_id == user_id
    ).order_by(desc(HistorialChat.timestamp)).limit(limite).all()

    mensajes = mensajes[::-1]

    texto_historial = ""
    if mensajes:
        texto_historial = "\n--- HISTORIAL DE CONVERSACION RECIENTE ---\n"
        for msg in mensajes:
            rol = "Usuario" if msg.role == "user" else "Asistente"
            texto_historial += f"{rol}: {msg.content}\n"
        texto_historial += "--- FIN DEL HISTORIAL ---\n"

    return texto_historial


def guardar_interaccion(user_id: int, pregunta: str, respuesta: str, db: Session):
    """Guarda la pregunta del usuario y la respuesta de la IA en la base de datos."""
    if not user_id:
        return

    try:
        msg_user = HistorialChat(
            user_id=user_id,
            role="user",
            content=pregunta
        )
        db.add(msg_user)
        msg_bot = HistorialChat(
            user_id=user_id,
            role="model",
            content=respuesta
        )
        db.add(msg_bot)
        db.commit()
    except Exception as e:
        print(f"Error guardando historial: {e}")


# ==========================================
# FUNCIONES AUXILIARES DE LOGICA
# ==========================================

def check_local_intent(text: str, db: Session):
    """
    Verifica intenciones básicas y palabras clave para proporcionar
    respuestas instantáneas sin consultar a la IA.
    """
    text = text.lower().strip()

    # --- SALUDOS ---
    saludos = ["hola", "buenos dias", "buenas", "que tal"]
    if any(x in text for x in saludos):
        return (
            "Hola! Soy el asistente de ESCOM Review Hub. "
            "¿En qué materia te puedo ayudar hoy?"
        )

    # --- IDENTIDAD ---
    if "quien te creo" in text or "que es esto" in text:
        return "Soy el asistente virtual de ESCOM Review Hub."

    if "genero te identificas" in text or "cual es tu genero" in text:
        return "Amigo, soy una IA, no tengo género ni sentimientos."

    # --- ESTADISTICAS ---
    if "cuantas materias" in text:
        count = db.query(main_models.Materia).count()
        return f"Tenemos {count} materias registradas."

    if "cuantos profesores" in text:
        count = db.query(main_models.Profesor).count()
        return f"Hay {count} profesores registrados."

    # --- FUNCIONALIDADES PLATAFORMA ---
    if "subo un archivo" in text or "puedo subir un archivo" in text:
        return (
            "Para subir un recurso, ve a la sección del Portal "
            "Estudiantil y selecciona la materia."
        )

    pass_keys = [
        "cambiar contraseña", "olvidé mi contraseña", "recuperar contraseña"
    ]
    if any(k in text for k in pass_keys):
        return (
            "Puedes restablecer tu contraseña haciendo click aquí: "
            "[LINK_RECUPERAR_PASS]"
        )

    # --- ESCOM INFO ---
    if "justificantes" in text or "subir justificante" in text:
        return (
            "Puedes gestionar tu justificante en este enlace: "
            "[LINK_JUSTIFICANTES_ESCOM]"
        )

    loc_keys = ["donde esta escom", "ubicacion de escom", "direccion"]
    if any(k in text for k in loc_keys):
        return (
            "ESCOM se encuentra en Av. IPN 2580, Nueva Industrial Vallejo, "
            "GAM, CDMX, C.P. 07738."
        )

    calif_keys = [
        "dia calificaciones", "cuando salen las calificaciones",
        "fecha limite calificaciones"
    ]
    if any(k in text for k in calif_keys):
        return (
            "Según el calendario, el último día del semestre 2025-2 "
            "es el 16/01/25."
        )

    ets_keys = ["cuando son los ets", "fecha de los ets", "dia de los ets"]
    if any(k in text for k in ets_keys):
        return (
            "Las fechas de ETS están en el calendario oficial. "
            "Recuerda generar tu línea de captura en el SAES."
        )

    english_keys = ["cursos de inglés", "celex", "ingles"]
    if any(k in text for k in english_keys):
        return (
            "El CELEX ESCOM ofrece cursos. Revisa su Facebook o la web "
            "oficial para las convocatorias."
        )

    health_keys = ["me siento mal", "servicio medico", "enfermeria"]
    if any(k in text for k in health_keys):
        return (
            "Puedes acudir al consultorio médico de ESCOM en el "
            "edificio de servicios escolares."
        )

    # --- EASTER EGGS ---
    jokes_keys = ["sentido de la vida", "chiste", "hazme reir"]
    if any(k in text for k in jokes_keys):
        return (
            "El sentido de la vida es que tu código compile sin warnings. "
            "¡Sigue estudiando!"
        )

    return None


def detectar_materia_automatica(texto: str, db: Session):
    """
    Intenta detectar el nombre de una materia dentro de un texto dado
    usando intersección de palabras clave.
    """
    texto = texto.lower()
    # Tokenizamos el texto del usuario (palabras sueltas)
    tokens_usuario = set(re.findall(r'\w+', texto))

    materias = db.query(
        main_models.Materia.id, main_models.Materia.nombre
    ).all()

    candidato = None
    max_matches = 0

    for mat_id, mat_nombre in materias:
        nombre_clean = mat_nombre.lower()

        # 1. Coincidencia Exacta (Prioridad Maxima)
        if nombre_clean in texto:
            return mat_id, mat_nombre

        # 2. Coincidencia por palabras (Intersección de conjuntos)
        tokens_materia = set(re.findall(r'\w+', nombre_clean))
        # Filtramos palabras irrelevantes cortas (de, la, i, ii)
        tokens_importantes = {t for t in tokens_materia if len(t) > 2}

        if not tokens_importantes:
            continue

        coincidencias = len(tokens_usuario.intersection(tokens_importantes))

        # Necesitamos al menos una palabra relevante coincidente
        if coincidencias > 0:
            if coincidencias > max_matches:
                max_matches = coincidencias
                candidato = (mat_id, mat_nombre)

    return candidato if candidato else (None, None)


def generar_y_guardar_recursos_auto(
    materia_id: int, materia_nombre: str, db: Session
):
    """
    Utiliza la IA para generar sugerencias de recursos académicos
    cuando una materia no tiene materiales registrados.
    """
    print(f"IA: Generando recursos para '{materia_nombre}'...")

    prompt = (
        f'Actúa como profesor experto de: "{materia_nombre}". '
        'Genera 3 recursos.\n'
        'Descripciones MUY BREVES (Max 20 palabras).\n'
        'JSON FORMAT:\n'
        '[{"titulo": "X", "tipo": "video/pdf/link", '
        '"url": "url", "desc": "txt"}]'
    )

    json_text = generate_smart(prompt)

    try:
        clean_text = json_text.replace(
            "```json", ""
        ).replace("```", "").strip()
        match = re.search(r'\[.*\]', clean_text, re.DOTALL)
        if match:
            clean_text = match.group(0)

        datos = json.loads(clean_text)
        nuevos_recursos = []

        tipo_map = {
            "video": study_models.ResourceType.VIDEO,
            "pdf": study_models.ResourceType.PDF,
            "link": study_models.ResourceType.LINK
        }

        # --- CAMBIO: OBTENER ID DEL SISTEMA DESDE ENV ---
        system_user_id = int(os.getenv("SYSTEM_USER_ID", "1"))

        for item in datos:
            desc_segura = item.get("desc", "Generado por Gemini")[:250]

            nuevo = study_models.Resource(
                title=item.get("titulo", "Recurso IA"),
                description=desc_segura,
                type=tipo_map.get(
                    item.get("tipo"),
                    study_models.ResourceType.LINK
                ),
                url_or_path=item.get("url", "#"),
                content_text=f"Recurso recomendado: {item.get('desc')}",
                materia_id=materia_id,
                user_id=system_user_id
            )
            db.add(nuevo)
            nuevos_recursos.append(nuevo)

        db.commit()
        return nuevos_recursos

    except Exception as e:
        print(f"Error guardando recursos IA: {e}")
        db.rollback()
        return []


# ==========================================
# ENDPOINT PRINCIPAL
# ==========================================

router = APIRouter()


@router.post("/preguntar", response_model=esquemas.RespuestaChat)
def preguntar_al_bot(
    pregunta: esquemas.PreguntaChat,
    db: Session = Depends(get_db)
):
    """
    Endpoint principal para interactuar con el Chatbot. Maneja límites,
    historial, detección de materia y generación de respuestas.
    """
    user_query = pregunta.texto
    user_id = pregunta.user_id
    materia_actual_id = pregunta.materia_id
    nombre_materia_detectada = None

    # 1. Verificar Limite
    puede_preguntar = verificar_limite_usuario(user_id, db)
    if not puede_preguntar:
        return {
            "respuesta": (
                "Me tengo que retirar por el momento, he alcanzado "
                "mi límite de respuestas por hoy."
            )
        }

    # 2. Recuperar Historial
    historial_contexto = recuperar_historial(user_id, db)

    # 3. Deteccion de Materia (Si no viene en el request)
    if not materia_actual_id:
        det_id, det_nom = detectar_materia_automatica(user_query, db)
        if det_id:
            materia_actual_id = det_id
            nombre_materia_detectada = det_nom

    # 4. Logica Local (Respuestas rapidas)
    if not materia_actual_id:
        local_resp = check_local_intent(user_query, db)
        if local_resp:
            guardar_interaccion(user_id, user_query, local_resp, db)
            return {"respuesta": local_resp}

    # 5. Modo Soporte General (Sin materia)
    if not materia_actual_id:
        prompt = (
            f"Eres el asistente de ESCOM Review Hub.\n{historial_contexto}\n"
            f"Usuario: '{user_query}'\n"
            "Responde brevemente. Si es duda académica, pide la materia."
        )
        resp = generate_smart(prompt)
        guardar_interaccion(user_id, user_query, resp, db)
        return {"respuesta": resp}

    # 6. Modo Estudio (Con materia identificada)
    recursos = db.query(study_models.Resource).filter(
        study_models.Resource.materia_id == materia_actual_id
    ).all()

    mensaje_sistema = ""
    if not recursos:
        if not nombre_materia_detectada:
            mat_obj = db.query(main_models.Materia).filter(
                main_models.Materia.id == materia_actual_id
            ).first()
            nombre_materia_detectada = (
                mat_obj.nombre if mat_obj else "Materia"
            )

        recursos = generar_y_guardar_recursos_auto(
            materia_actual_id, nombre_materia_detectada, db
        )
        mensaje_sistema = "He buscado nuevas referencias para ti.\n"

    # Contexto visual limitado (Max 1000 chars por recurso)
    lista_links = []
    contexto_recursos = ""
    for res in recursos:
        texto_limpio = (res.content_text or "")[:1000]
        contexto_recursos += f"--- {res.title} ---\n{texto_limpio}\n"
        lista_links.append(f"🔗 [{res.title}]({res.url_or_path})")

    texto_links = "\n".join(lista_links[:5])

    # 7. Modo Turbo (Solo links)
    keywords_recursos = ["recursos", "material", "links", "bibliografia"]
    if any(k in user_query.lower() for k in keywords_recursos) and recursos:
        resp_turbo = (
            f"Aquí tienes los materiales para "
            f"{nombre_materia_detectada}:\n\n{texto_links}"
        )
        guardar_interaccion(user_id, user_query, resp_turbo, db)
        return {"respuesta": resp_turbo}

    # 8. Generacion IA con Contexto
    prompt = (
        "Eres un tutor experto.\n"
        f"{mensaje_sistema}\n"
        f"{historial_contexto}\n"
        "INFORMACIÓN DE REFERENCIA:\n"
        f"{contexto_recursos}\n"
        f"PREGUNTA: '{user_query}'\n"
        "Responde usando las referencias si sirven."
    )

    respuesta_ia = generate_smart(prompt)
    respuesta_final = f"{respuesta_ia}\n\n**Fuentes:**\n{texto_links}"

    guardar_interaccion(user_id, user_query, respuesta_final, db)
    return {"respuesta": respuesta_final}
