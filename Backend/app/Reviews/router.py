from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import dependencias
from app.Creacion_mats_prof import crud as crud_catalogos
from app.Creacion_mats_prof import modelos as catalogos_models
from app.Creacion_mats_prof import esquemas as catalogo_esquemas
from app.Creacion_mats_prof import crud as catalogo_crud
from app.database import get_db
from app.Reviews import crud, esquemas
from app.Usuarios import esquemas as user_schemas

router = APIRouter()


@router.post("/resenas/", response_model=esquemas.Resena)
def crear_resena(
    resena: esquemas.ResenaCreate,
    db: Session = Depends(get_db),
    current_user: user_schemas.UserResponse = Depends(
        dependencias.get_current_user
    )
):
    """
    Crea una nueva reseña en el sistema.

    Realiza validaciones previas para asegurar que tanto la materia
    (por nombre) como el profesor (por ID) existan en la base de datos
    antes de registrar la opinión.
    """
    # 1. Validar Materia (Debe existir sí o sí)
    materia_db = crud_catalogos.get_materia_by_name(db, resena.materia_nombre)
    if not materia_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"La materia '{resena.materia_nombre}' no existe. "
                "Selecciona una de la lista."
            )
        )

    # 2. Lógica Inteligente de Profesor
    profesor_final_id = resena.profesor_id

    # CASO A: Se seleccionó un profesor existente (ID > 0)
    if profesor_final_id > 0:
        profesor_db = db.query(catalogos_models.Profesor).filter(
            catalogos_models.Profesor.id == profesor_final_id
        ).first()
        if not profesor_db:
            raise HTTPException(
                status_code=404,
                detail="El profesor seleccionado no existe."
            )

    # CASO B: Se quiere crear uno nuevo (ID = 0 y hay nombre)
    elif resena.profesor_nombre_nuevo:
        # Verificar si ya existe por nombre para no duplicar
        nombre_limpio = resena.profesor_nombre_nuevo.strip()
        profesor_existente = db.query(catalogos_models.Profesor).filter(
            catalogos_models.Profesor.nombre.ilike(nombre_limpio)
        ).first()

        if profesor_existente:
            profesor_final_id = profesor_existente.id
        else:
            # Crear el nuevo profesor
            nuevo_profe_data = catalogo_esquemas.ProfesorCreate(
                nombre=nombre_limpio
            )
            nuevo_profe = catalogo_crud.create_profesor(db, nuevo_profe_data)
            profesor_final_id = nuevo_profe.id

    else:
        raise HTTPException(
            status_code=400,
            detail="Debes seleccionar un profesor o escribir un nombre nuevo."
        )

    # 3. Crear la reseña
    resena.profesor_id = profesor_final_id

    return crud.create_resena(
        db=db,
        resena=resena,
        materia_id=materia_db.id,
        user_id=current_user.id
    )


@router.get("/resenas/", response_model=List[esquemas.Resena])
def leer_resenas(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Obtiene una lista paginada de todas las reseñas registradas."""
    return crud.get_resenas(db, skip=skip, limit=limit)


@router.post("/votar", response_model=esquemas.VotoResponse)
def votar_comentario(
    voto: esquemas.VotoCreate,
    db: Session = Depends(get_db),
    current_user: user_schemas.UserResponse = Depends(
        dependencias.get_current_user
    )
):
    """Registra un voto de utilidad sobre una reseña específica."""
    total, accion = crud.votar_resena(
        db=db,
        resena_id=voto.resena_id,
        user_id=current_user.id,
        es_util=voto.es_util
    )

    mensajes = {
        "registrado": "Voto registrado correctamente",
        "eliminado": "Voto eliminado",
        "actualizado": "Voto actualizado"
    }

    msg = mensajes.get(accion, "Accion realizada")

    return {"mensaje": msg, "total_utiles": total}
