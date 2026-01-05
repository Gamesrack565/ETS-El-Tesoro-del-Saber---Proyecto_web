from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.Creacion_mats_prof.modelos import Materia, Profesor
from app.database import get_db
from app.Estadistica import esquemas
from app.Porta_Estudio.modelos import Resource
from app.Reviews.modelos import Resena
from app.Usuarios.modelos import User

router = APIRouter()


@router.get("/general", response_model=esquemas.StatsGeneral)
def estadisticas_generales(db: Session = Depends(get_db)):
    """
    Obtiene los contadores totales de las entidades principales del sistema.

    Se utiliza para poblar las tarjetas de estadísticas en el panel de
    control (dashboard) principal.

    Args:
        db (Session): Sesion de base de datos.

    Returns:
        StatsGeneral: Objeto con los totales de usuarios, reseñas,
        recursos, profesores y materias.
    """
    return {
        "usuarios": db.query(User).count(),
        "resenas": db.query(Resena).count(),
        "recursos": db.query(Resource).count(),
        "profesores": db.query(Profesor).count(),
        "materias": db.query(Materia).count(),
    }


@router.get("/top-profesores")
def mejores_profesores(limit: int = 5, db: Session = Depends(get_db)):
    """
    Obtiene el ranking de los profesores con mejor calificacion promedio.

    Args:
        limit (int): Cantidad de profesores a mostrar (Top N).
        db (Session): Sesion de base de datos.

    Returns:
        List[ItemRanking]: Lista ordenada de profesores con su promedio.
    """
    # Consulta de agregacion:
    # 1. Selecciona nombre, promedio de calificacion y total de reseñas.
    # 2. Une con la tabla de reseñas.
    # 3. Agrupa los resultados por ID del profesor.
    # 4. Filtra aquellos que tengan al menos 1 reseña.
    # 5. Ordena descendente por el promedio calculado.
    # 1. Tu consulta original para obtener el Top
    resultados = db.query(
        # Agregamos el ID para poder buscar sus reseñas luego
        Profesor.id,
        Profesor.nombre,
        func.avg(Resena.calificacion).label("promedio"),
        func.count(Resena.id).label("total")
    ).join(Resena).group_by(
        Profesor.id
    ).having(
        func.count(Resena.id) > 0
    ).order_by(
        desc("promedio")
    ).limit(limit).all()

    # 2. Procesamos la lista para agregar el "comentario destacado"
    lista_final = []
    for r in resultados:
        # Buscamos la reseña más reciente de este profesor específico
        ultima_resena = db.query(Resena).filter(
            Resena.profesor_id == r.id,
            Resena.comentario.is_not(None),  # Que tenga texto
            Resena.comentario != ""
        ).order_by(desc(Resena.id)).first()

        # Recortamos el comentario si es muy largo
        comentario_texto = "Sin comentarios aún"
        if ultima_resena and ultima_resena.comentario:
            comentario_texto = ultima_resena.comentario
            if len(comentario_texto) > 60:
                comentario_texto = comentario_texto[:60] + "..."

        lista_final.append({
            "nombre": r.nombre,
            "valor": round(r.promedio, 1),
            "total_resenas": r.total,
            "ultimo_comentario": comentario_texto  # <--- Campo Nuevo
        })

    return lista_final


@router.get(
    "/actividad-reciente",
    response_model=List[esquemas.ActividadReciente]
)
def actividad_reciente(db: Session = Depends(get_db)):
    """
    Obtiene las ultimas reseñas creadas en la plataforma.

    Args:
        db (Session): Sesion de base de datos.

    Returns:
        List[ActividadReciente]: Lista de las ultimas 5 reseñas.
    """
    # Obtenemos las últimas 5 reseñas con el objeto completo
    resenas = db.query(Resena).order_by(desc(Resena.id)).limit(5).all()

    return [
        {
            "id": r.id,
            "profesor": r.profesor.nombre if r.profesor else "Desconocido",
            "materia": r.materia.nombre if r.materia else "General",
            "calificacion": r.calificacion,
            "dificultad": r.dificultad,
            "total_votos_utiles": r.total_votos_utiles,
            "comentario": r.comentario,
        }
        for r in resenas
    ]
