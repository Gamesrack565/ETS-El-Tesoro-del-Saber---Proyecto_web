from typing import Optional

from pydantic import BaseModel

from app.Creacion_mats_prof.esquemas import Materia, Profesor


# --- ESQUEMAS DE RESEÑAS ---

class ResenaBase(BaseModel):
    """
    Esquema base para una Reseña.

    Define los datos fundamentales del contenido de la opinión.

    Atributos:
        comentario (Optional[str]): Texto de la reseña (puede ser nulo).
        calificacion (float): Puntuación numérica (generalmente 0-10).
        dificultad (int): Nivel de dificultad percibido (generalmente 1-10).
    """
    comentario: Optional[str] = None
    calificacion: float
    dificultad: int


class ResenaCreate(ResenaBase):
    """
    Esquema para la creación de una nueva reseña.

    Requiere identificar al profesor por ID y la materia por nombre
    (ya que el sistema buscará o validará la materia existente).

    Atributos:
        profesor_id (int): ID del profesor evaluado.
        materia_nombre (str): Nombre de la materia cursada.
    """
    profesor_id: int
    materia_nombre: str
    profesor_nombre_nuevo: Optional[str] = None


class Resena(ResenaBase):
    """
    Esquema de respuesta para una Reseña completa.

    Incluye metadatos del sistema, el usuario autor y objetos anidados
    completos del profesor y la materia para facilitar la visualización.

    Atributos:
        id (int): ID único de la reseña.
        user_id (int): ID del autor.
        profesor (Profesor): Objeto completo del profesor.
        materia (Materia): Objeto completo de la materia.
        total_votos_utiles (int): Contador de votos positivos recibidos.
    """
    id: int
    user_id: int
    profesor: Profesor
    materia: Materia
    total_votos_utiles: int = 0

    class Config:
        from_attributes = True


# --- ESQUEMAS DE VOTOS ---

class VotoCreate(BaseModel):
    """
    Esquema para emitir un voto sobre una reseña.

    Atributos:
        resena_id (int): ID de la reseña objetivo.
        es_util (bool): True = Like (Útil), False = Dislike (No útil).
    """
    resena_id: int
    es_util: bool


class VotoResponse(BaseModel):
    """
    Esquema de respuesta tras realizar una votación.

    Devuelve el estado actualizado para que el frontend refresque el contador.

    Atributos:
        mensaje (str): Descripción de la acción realizada.
        total_utiles (int): Nuevo total de votos útiles de la reseña.
    """
    mensaje: str
    total_utiles: int
