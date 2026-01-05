from sqlalchemy.orm import Session
from app.Creacion_mats_prof import esquemas, modelos


def get_profesores(db: Session, skip: int = 0, limit: int = 100):
    """
    Obtiene una lista de profesores con paginación.
    """
    return db.query(modelos.Profesor).offset(skip).limit(limit).all()


def create_profesor(db: Session, profesor: esquemas.ProfesorCreate):
    """
    Crea un nuevo profesor en la base de datos.
    """
    nombre_limpio = profesor.nombre.strip()
    db_profesor = modelos.Profesor(nombre=nombre_limpio)
    db.add(db_profesor)
    db.commit()
    db.refresh(db_profesor)
    return db_profesor


def get_profesor_by_name(db: Session, nombre: str):
    """
    Obtiene un profesor por nombre con búsqueda parcial
    """
    return db.query(modelos.Profesor).filter(
        modelos.Profesor.nombre.ilike(f"%{nombre}%")
    ).first()


# --- GESTION DE MATERIAS ---

def get_materias(db: Session, skip: int = 0, limit: int = 100):
    """
    Obtiene una lista de materias con paginación.
    """
    return db.query(modelos.Materia).offset(skip).limit(limit).all()


def create_materia(db: Session, materia: esquemas.MateriaCreate):
    """
    Crea una nueva materia en la base de datos.
    """
    nombre_limpio = materia.nombre.strip()
    db_materia = modelos.Materia(nombre=nombre_limpio)
    db.add(db_materia)
    db.commit()
    db.refresh(db_materia)
    return db_materia


def get_materia_by_name(db: Session, nombre: str):
    """
    Busca una materia por nombre EXACTO.
    """
    materia_exacta = db.query(modelos.Materia).filter(
        modelos.Materia.nombre.ilike(f"{nombre}")
    ).first()

    return materia_exacta
