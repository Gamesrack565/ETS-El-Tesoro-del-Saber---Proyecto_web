# Version 1.0
# Archivo: Chatbot/modelos.py
# Descripcion: Modelo de Base de Datos para el historial de chat con la IA.

from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from app.database import Base


class HistorialChat(Base):
    """
    Modelo de Base de Datos para el historial de chat con la IA.

    Almacena los mensajes individuales intercambiados entre el usuario
    y el modelo de IA para mantener la memoria de la conversacion.

    Atributos:
        id (int): Identificador unico del mensaje.
        user_id (int): Clave foranea que referencia al usuario propietario.
        role (str): Rol del emisor del mensaje ('user' o 'model').
        content (str): Contenido textual del mensaje.
        timestamp (datetime): Fecha y hora de creacion (UTC).
    """
    __tablename__ = "historial_chat"

    id = Column(Integer, primary_key=True, index=True)
    
    # Relacion con la tabla de usuarios (users.id)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Rol del mensaje: "user" (pregunta) o "model" (respuesta IA)
    role = Column(String(20), nullable=False)
    
    # Contenido del mensaje. Se usa Text para permitir respuestas largas.
    content = Column(Text, nullable=False)
    
    # Fecha de creacion por defecto en UTC
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relacion ORM para acceder al objeto User desde el historial.
    # Se usa string para evitar importaciones circulares.
    usuario = relationship("app.Usuarios.modelos.User")