from sqlalchemy.orm import Session

from app.Reviews import esquemas, modelos
from app.Reviews.modelos import Voto


# --- GESTION DE RESEÑAS ---

def get_resenas(db: Session, skip: int = 0, limit: int = 100):
    """
    Obtiene una lista paginada de todas las reseñas.

    Args:
        db (Session): Sesión de la base de datos.
        skip (int): Número de registros a saltar.
        limit (int): Límite de registros a devolver.

    Returns:
        List[Resena]: Lista de objetos Resena.
    """
    return db.query(modelos.Resena).offset(skip).limit(limit).all()


def create_resena(
    db: Session,
    resena: esquemas.ResenaCreate,
    materia_id: int,
    user_id: int
):
    """
    Crea una nueva reseña en la base de datos.

    Args:
        db (Session): Sesión de la base de datos.
        resena (ResenaCreate): Esquema con datos de la reseña.
        materia_id (int): ID de la materia asociada.
        user_id (int): ID del usuario autor.

    Returns:
        Resena: El objeto creado.
    """
    db_resena = modelos.Resena(
        comentario=resena.comentario,
        calificacion=resena.calificacion,
        dificultad=resena.dificultad,
        profesor_id=resena.profesor_id,
        materia_id=materia_id,
        user_id=user_id
    )
    db.add(db_resena)
    db.commit()
    db.refresh(db_resena)
    return db_resena


# --- GESTION DE VOTOS ---

def votar_resena(db: Session, resena_id: int, user_id: int, es_util: bool):
    """
    Registra, actualiza o elimina un voto de utilidad en una reseña.

    Implementa lógica de "Toggle":
    - Si no hay voto: Crea uno nuevo.
    - Si ya hay voto igual: Lo elimina (quita el like/dislike).
    - Si hay voto diferente: Lo actualiza.

    Args:
        db (Session): Sesión de base de datos.
        resena_id (int): ID de la reseña a votar.
        user_id (int): ID del usuario que vota.
        es_util (bool): True para 'Útil', False para 'No útil'.

    Returns:
        tuple: (total_votos_utiles, accion_realizada)
    """
    # 1. Buscamos si ya existe un voto previo de este usuario para esta reseña
    voto_existente = db.query(Voto).filter(
        Voto.resena_id == resena_id,
        Voto.user_id == user_id
    ).first()

    accion = "registrado"

    if voto_existente:
        # LOGICA DE CONMUTACION (TOGGLE):
        # Si el usuario intenta votar lo mismo que ya tenia,
        # se interpreta como cancelar el voto (borrarlo).
        if voto_existente.es_util == es_util:
            db.delete(voto_existente)
            accion = "eliminado"
        else:
            # Si cambia de opinion (Like -> Dislike), actualizamos el registro
            voto_existente.es_util = es_util
            accion = "actualizado"
    else:
        # Si es un voto nuevo, creamos el registro
        nuevo_voto = Voto(
            resena_id=resena_id,
            user_id=user_id,
            es_util=es_util
        )
        db.add(nuevo_voto)

    db.commit()

    # 2. Recalculamos totales de votos positivos para devolver al frontend
    total = db.query(Voto).filter(
        Voto.resena_id == resena_id,
        Voto.es_util == True  # noqa: E712 (SQLAlchemy requiere == True)
    ).count()

    return total, accion
