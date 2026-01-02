from pydantic import BaseModel


class StatsGeneral(BaseModel):
    """
    Esquema de datos para las estadisticas generales del sistema.

    Se utiliza para enviar al dashboard los contadores totales de las
    principales entidades de la plataforma.

    Atributos:
        usuarios (int): Numero total de usuarios registrados.
        resenas (int): Numero total de reseñas publicadas.
        recursos (int): Numero total de recursos de estudio subidos.
        profesores (int): Numero total de profesores en el catalogo.
        materias (int): Numero total de materias en el catalogo.
    """
    usuarios: int
    resenas: int
    recursos: int
    profesores: int
    materias: int


class ItemRanking(BaseModel):
    """
    Esquema para representar un elemento dentro de una lista de ranking.

    Se usa tanto para listas de 'Mejores Profesores' como para
    'Materias mas dificiles', estandarizando la estructura visual.

    Atributos:
        nombre (str): Nombre del profesor o materia.
        valor (float): La metrica principal (promedio de calificacion o
                       nivel de dificultad).
        total_resenas (int): Cantidad de reseñas en las que se basa el valor.
    """
    nombre: str
    valor: float
    total_resenas: int


class ActividadReciente(BaseModel):
    """
    Esquema para mostrar un resumen de actividad reciente en el dashboard.

    Representa una tarjeta simplificada de una reseña recien creada.

    Atributos:
        profesor (str): Nombre del profesor calificado.
        materia (str): Nombre de la materia asociada.
        calificacion (float): Calificacion otorgada en la reseña.
        comentario_corto (str): Extracto truncado del comentario original.
    """
    profesor: str
    materia: str
    calificacion: float
    comentario_corto: str
