import re
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import dependencias
from app.Creacion_mats_prof import crud, esquemas, modelos
from app.database import get_db
from app.Usuarios import esquemas as user_schemas

router = APIRouter()

# --- FILTRO DE GROSERIAS (LISTA NEGRA) ---
# Se utiliza un conjunto (set) para busquedas O(1) de alta eficiencia.
PALABRAS_PROHIBIDAS = {
    "puto", "puta", "verga", "pendejo", "pendeja", "mierda",
    "cabron", "cabrona", "mamada", "culo", "pinche", "imbecil",
    "idiota", "estupido", "estupida", "zorra", "perra", "joto",
    "maricon", "verguero", "chinga", "chingada", "retrasado"
}


def validar_texto_limpio(texto: str):
    """
    Valida que el texto ingresado cumpla con normas de comunidad y formato.

    Realiza dos validaciones principales:
    1. Longitud minima del texto.
    2. Ausencia de lenguaje inapropiado (groserias).

    Args:
        texto (str): El nombre del profesor o materia a validar.

    Raises:
        HTTPException (400): Si el texto es muy corto o contiene malas palabras
    """
    texto_lower = texto.lower()

    # 1. Chequeo de longitud minima
    if len(texto) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            # Se dividen las cadenas largas para cumplir PEP 8 (E501)
            detail=(
                "El nombre es demasiado corto. "
                "Minimo 3 caracteres."
            )
        )

    # 2. Chequeo de groserias
    # Dividimos por espacios o caracteres no alfanumericos para analizar
    # palabra por palabra y evitar evasiones simples.
    palabras = re.split(r'\W+', texto_lower)

    for palabra in palabras:
        if palabra in PALABRAS_PROHIBIDAS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"El sistema detecto lenguaje inapropiado: '{palabra}'. "
                    "Por favor se respetuoso."
                )
            )


# --- RUTAS PARA PROFESORES ---

@router.post("/profesores/", response_model=esquemas.Profesor)
def crear_profesor(
    profesor: esquemas.ProfesorCreate,
    db: Session = Depends(get_db),
    current_user: user_schemas.UserResponse = Depends(
        dependencias.get_current_user
    )
):
    """
    Registra un nuevo profesor en la base de datos.

    Cualquier usuario autenticado puede crear un profesor si no existe.

    Args:
        profesor (ProfesorCreate): Datos del profesor.
        db (Session): Sesion de BD.
        current_user (UserResponse): Usuario logueado.

    Returns:
        Profesor: El objeto creado.
    """
    # 1. Filtro de contenido inapropiado
    validar_texto_limpio(profesor.nombre)

    # 2. Validar duplicados (Anti-spam)
    # Se normaliza el texto eliminando espacios extra antes de buscar.
    existe = db.query(modelos.Profesor).filter(
        modelos.Profesor.nombre.ilike(profesor.nombre.strip())
    ).first()

    if existe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El profesor '{profesor.nombre}' ya existe."
        )

    return crud.create_profesor(db=db, profesor=profesor)


@router.get("/profesores/", response_model=List[esquemas.Profesor])
def leer_profesores(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Obtiene la lista de profesores registrados con paginacion.

    Args:
        skip (int): Registros a saltar.
        limit (int): Limite de registros.
        db (Session): Sesion de BD.

    Returns:
        List[Profesor]: Lista de profesores.
    """
    return crud.get_profesores(db, skip=skip, limit=limit)


# --- RUTAS PARA MATERIAS ---

@router.post("/materias/", response_model=esquemas.Materia)
def crear_materia(
    materia: esquemas.MateriaCreate,
    db: Session = Depends(get_db),
    current_user: user_schemas.UserResponse = Depends(
        dependencias.get_current_user
    )
):
    """
    Registra una nueva materia en la base de datos.

    Cualquier usuario autenticado puede crear una materia si no existe.

    Args:
        materia (MateriaCreate): Datos de la materia.
        db (Session): Sesion de BD.
        current_user (UserResponse): Usuario logueado.

    Returns:
        Materia: El objeto creado.
    """
    # 1. Filtro de contenido inapropiado
    validar_texto_limpio(materia.nombre)

    # 2. Validar duplicados
    existe = db.query(modelos.Materia).filter(
        modelos.Materia.nombre.ilike(materia.nombre.strip())
    ).first()

    if existe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"La materia '{materia.nombre}' ya existe."
        )

    return crud.create_materia(db=db, materia=materia)


@router.get("/materias/", response_model=List[esquemas.Materia])
def leer_materias(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Obtiene la lista de materias registradas con paginacion.

    Args:
        skip (int): Registros a saltar.
        limit (int): Limite de registros.
        db (Session): Sesion de BD.

    Returns:
        List[Materia]: Lista de materias.
    """
    return crud.get_materias(db, skip=skip, limit=limit)
