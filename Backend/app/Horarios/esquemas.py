from typing import List, Optional

from pydantic import BaseModel


# --- ESQUEMAS PARA ITEMS (MATERIAS INDIVIDUALES) ---

class ItemBase(BaseModel):
    """
    Esquema base para un elemento individual dentro del horario.

    Representa la relación entre una materia y su franja horaria.

    Atributos:
        materia_id (int): ID de la materia en el catálogo.
        hora_grupo (Optional[str]): Horario en formato texto.
    """
    materia_id: int
    hora_grupo: Optional[str] = None


class ItemCreate(ItemBase):
    """
    Esquema para la creación de un item.

    Hereda de ItemBase sin campos adicionales.
    """
    pass


class ItemResponse(ItemBase):
    """
    Esquema de respuesta para un item de horario.

    Incluye información enriquecida como el nombre de la materia
    para facilitar la visualización en el frontend.

    Atributos:
        id (int): ID único del item en la base de datos.
        materia_nombre (Optional[str]): Nombre legible de la materia asociada.
    """
    id: int
    materia_nombre: Optional[str] = None

    class Config:
        from_attributes = True


# --- ESQUEMAS PARA HORARIOS (CONTENEDORES) ---

class HorarioCreate(BaseModel):
    """
    Esquema para crear un nuevo horario completo.

    Atributos:
        nombre (str): Nombre personalizado para el horario (ej: "Opción A").
        items (List[ItemCreate]): Lista de materias y horas que componen
                                  este horario.
    """
    nombre: str
    items: List[ItemCreate] = []


class HorarioResponse(BaseModel):
    """
    Esquema de respuesta para un horario completo.

    Devuelve la estructura jerárquica: Horario -> Lista de Items.

    Atributos:
        id (int): ID único del horario.
        nombre (str): Nombre del horario.
        items (List[ItemResponse]): Lista de materias asociadas.
    """
    id: int
    nombre: str
    items: List[ItemResponse] = []

    class Config:
        from_attributes = True
