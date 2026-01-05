from typing import Optional
from pydantic import BaseModel


class PreguntaChat(BaseModel):
    """
    Modelo de datos para la entrada de una pregunta al chatbot.

    Define la estructura del JSON que el frontend debe enviar para realizar
    una consulta a la IA.

    Atributos:
        texto (str): La consulta o pregunta en lenguaje natural.
        materia_id (Optional[int]): ID de la materia para dar contexto
            específico (opcional).
        user_id (Optional[int]): ID del usuario que realiza la pregunta.
            Permite mantener historial de conversación.
    """
    texto: str
    materia_id: Optional[int] = None
    # Si user_id es None, el sistema lo trata como un usuario "Invitado"
    # y no guarda el historial de la conversacion en la base de datos.
    user_id: Optional[int] = None


class RespuestaChat(BaseModel):
    """
    Modelo de datos para la salida de la respuesta del chatbot.

    Define la estructura del JSON que el backend devuelve al frontend.

    Atributos:
        respuesta (str): El texto generado por la IA.
    """
    respuesta: str
