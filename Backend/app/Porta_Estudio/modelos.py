import enum

from sqlalchemy import Column, Enum, ForeignKey, Integer, String
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import relationship

from app.database import Base


class ResourceType(str, enum.Enum):
    """
    Enumeración para los tipos de recursos permitidos en la plataforma.
    """
    PDF = "pdf"
    VIDEO = "video"
    LINK = "link"
    IMAGE = "image"


class Resource(Base):
    """
    Modelo de Base de Datos para un Recurso de Estudio.

    Representa un archivo o enlace compartido por un usuario para una
    materia específica. Incluye un campo de texto largo para almacenar
    el contenido extraído (OCR) y potenciar el análisis con IA.

    Atributos:
        id (int): Identificador único del recurso.
        title (str): Título del recurso.
        description (str): Descripción breve.
        type (ResourceType): Tipo de archivo/enlace (PDF, Video, etc.).
        url_or_path (str): Ubicación del archivo o URL externa.
        content_text (str): Contenido textual extraído (para IA).
        materia_id (int): Clave foránea de la materia asociada.
        user_id (int): Clave foránea del usuario que subió el recurso.
    """
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150), nullable=False)
    description = Column(String(255), nullable=True)
    type = Column(Enum(ResourceType), nullable=False)
    url_or_path = Column(String(500), nullable=False)

    # Se usa LONGTEXT de MySQL para almacenar grandes cantidades de texto
    # extraído de PDFs o transcripciones, necesario para el contexto de la IA.
    content_text = Column(LONGTEXT, nullable=True)

    materia_id = Column(Integer, ForeignKey("materias.id"))
    user_id = Column(Integer, ForeignKey("users.id"))

    # Relación con la Materia (Mapeo a la carpeta Creacion_mats_prof)
    materia = relationship(
        "app.Creacion_mats_prof.modelos.Materia",
        back_populates="resources"
    )

    # Relación con el Usuario (Uploader)
    uploader = relationship("app.Usuarios.modelos.User")
