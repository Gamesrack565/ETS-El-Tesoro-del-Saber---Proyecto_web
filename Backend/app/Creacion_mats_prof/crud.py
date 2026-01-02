from sqlalchemy.orm import Session
# Ya no necesitamos 'thefuzz' si queremos ser estrictos
# from thefuzz import process 

from app.Creacion_mats_prof import esquemas, modelos


# --- GESTION DE PROFESORES ---

def get_profesores(db: Session, skip: int = 0, limit: int = 100):
    return db.query(modelos.Profesor).offset(skip).limit(limit).all()


def create_profesor(db: Session, profesor: esquemas.ProfesorCreate):
    nombre_limpio = profesor.nombre.strip()
    db_profesor = modelos.Profesor(nombre=nombre_limpio)
    db.add(db_profesor)
    db.commit()
    db.refresh(db_profesor)
    return db_profesor


def get_profesor_by_name(db: Session, nombre: str):
    # Para profesores podemos mantener el ilike con % si quieres búsqueda parcial,
    # o cambiarlo a estricto si prefieres. De momento lo dejo parcial.
    return db.query(modelos.Profesor).filter(
        modelos.Profesor.nombre.ilike(f"%{nombre}%")
    ).first()


# --- GESTION DE MATERIAS ---

def get_materias(db: Session, skip: int = 0, limit: int = 100):
    return db.query(modelos.Materia).offset(skip).limit(limit).all()


def create_materia(db: Session, materia: esquemas.MateriaCreate):
    nombre_limpio = materia.nombre.strip()
    db_materia = modelos.Materia(nombre=nombre_limpio)
    db.add(db_materia)
    db.commit()
    db.refresh(db_materia)
    return db_materia


def get_materia_by_name(db: Session, nombre: str):
    """
    Busca una materia por nombre EXACTO.
    Se ha eliminado la búsqueda difusa para evitar mezclar materias
    con nombres similares (ej. Cálculo vs Cálculo Aplicado).
    """
    
    # Busqueda exacta (Insensible a mayúsculas/minúsculas)
    # Al no usar los símbolos de porcentaje (%), 'ilike' busca la cadena completa exacta.
    materia_exacta = db.query(modelos.Materia).filter(
        modelos.Materia.nombre.ilike(f"{nombre}")
    ).first()

    return materia_exacta
    
    # --- SECCIÓN ELIMINADA ---
    # La lógica de 'thefuzz' se eliminó porque causaba que
    # "Cálculo" coincidiera con "Cálculo Aplicado".