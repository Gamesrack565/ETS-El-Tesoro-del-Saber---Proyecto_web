import re
from typing import List, Dict


def parse_whatsapp_chat(content: str) -> List[Dict[str, str]]:
    """
    Analiza el contenido de un archivo de texto exportado de WhatsApp.

    Soporta formatos de Android e iOS, asi como mensajes multilinea.
    Extrae la fecha, hora, autor y contenido del mensaje.

    Args:
        content (str): El contenido completo del archivo .txt del chat.

    Returns:
        List[Dict[str, str]]: Una lista de diccionarios, donde cada uno
        representa un mensaje con las claves:
        - 'timestamp': Fecha y hora del mensaje.
        - 'author': Nombre del remitente.
        - 'message': Contenido del mensaje.
    """
    parsed_messages = []

    # Regex optimizado para detectar encabezados de mensajes.
    # Soporta:
    # 1. Android/Web: "dd/mm/yyyy, hh:mm - Autor: Mensaje"
    # 2. iOS: "[dd/mm/yyyy, hh:mm:ss] Autor: Mensaje"
    # Grupos de captura:
    # (1) Fecha, (2) Hora, (3) Autor, (4) Mensaje inicial
    pattern = (
        r'^(?:\[?)(\d{1,2}/\d{1,2}/\d{2,4})[,\s].*?'
        r'(\d{1,2}:\d{2}(?::\d{2})?(?:\s?[ap]\.?\s?m\.?)?)(?:\]?)'
        r'\s(?:-|]?)\s(.*?):\s(.*)$'
    )

    lines = content.split('\n')
    current_message = None

    for line in lines:
        line = line.strip()

        # Saltar lineas vacias para evitar procesamiento innecesario
        if not line:
            continue

        # Validar si la linea corresponde al inicio de un nuevo mensaje
        match = re.match(pattern, line, re.IGNORECASE)

        if match:
            # Si existia un mensaje anterior procesandose, se guarda
            # antes de iniciar el nuevo.
            if current_message:
                parsed_messages.append(current_message)

            date, time_str, author, message_text = match.groups()

            current_message = {
                "timestamp": f"{date} {time_str}",
                "author": author.strip(),
                "message": message_text.strip()
            }

        else:
            # Logica de multilinea:
            # Si la linea no coincide con el patron de fecha/hora,
            # se asume que es la continuacion del mensaje anterior.
            if current_message:
                current_message["message"] += f"\n{line}"

    # Asegurar que el ultimo mensaje procesado se agregue a la lista
    if current_message:
        parsed_messages.append(current_message)

    return parsed_messages
