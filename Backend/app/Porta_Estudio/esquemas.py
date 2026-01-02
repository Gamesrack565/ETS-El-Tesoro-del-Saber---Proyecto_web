from typing import Optional

from pydantic import BaseModel

from app.Porta_Estudio.modelos import ResourceType


class ResourceBase(BaseModel):
    """
    Esquema base para un recurso de estudio.

    Define los atributos comunes que comparten tanto la creación como
    la respuesta de un recurso.

    Atributos:
        title (str): Título descriptivo del recurso.
        description (Optional[str]): Breve explicación del contenido.
        type (ResourceType): Tipo de recurso (PDF, Video, Link, etc.),
                             basado en el Enum definido en los modelos.
        url_or_path (str): URL externa o ruta local al archivo.
    """
    title: str
    description: Optional[str] = None
    type: ResourceType
    url_or_path: str


class ResourceCreate(ResourceBase):
    """
    Esquema para la creación de un nuevo recurso.

    Extiende ResourceBase añadiendo el ID de la materia a la que
    pertenece el recurso.

    Atributos:
        materia_id (int): ID de la materia asociada.
    """
    materia_id: int


class ResourceResponse(ResourceBase):
    """
    Esquema de respuesta para un recurso de estudio.

    Incluye los identificadores de base de datos y metadatos de relación.

    Atributos:
        id (int): Identificador único del recurso.
        user_id (int): ID del usuario que subió el recurso.
        materia_id (int): ID de la materia asociada.
    """
    id: int
    user_id: int
    materia_id: int

    class Config:
        from_attributes = True
