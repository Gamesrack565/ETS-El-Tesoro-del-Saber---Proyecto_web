from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import dependencias
from app.database import get_db
from app.Horarios import crud, esquemas
from app.Usuarios import esquemas as user_schemas

router = APIRouter()


@router.post("/", response_model=esquemas.HorarioResponse)
def crear_nuevo_horario(
    horario: esquemas.HorarioCreate,
    db: Session = Depends(get_db),
    current_user: user_schemas.UserResponse = Depends(
        dependencias.get_current_user
    )
):
    """
    Crea un nuevo horario y valida posibles choques de materias.

    Recibe un objeto con el nombre del horario y la lista de materias
    (items) con sus respectivas horas. Asocia el horario al usuario actual.

    Args:
        horario (HorarioCreate): Datos del horario a crear.
        db (Session): Sesion de base de datos.
        current_user (UserResponse): Usuario autenticado.

    Returns:
        HorarioResponse: El objeto horario creado con sus items.

    Ejemplo de JSON:
    {
      "nombre": "Opcion A - Manana",
      "items": [
         {"materia_id": 1, "hora_grupo": "7:00 - 8:30"},
         {"materia_id": 2, "hora_grupo": "8:30 - 10:00"}
      ]
    }
    """
    return crud.create_horario(
        db=db,
        horario=horario,
        user_id=current_user.id
    )


@router.get("/", response_model=List[esquemas.HorarioResponse])
def ver_mis_horarios(
    db: Session = Depends(get_db),
    current_user: user_schemas.UserResponse = Depends(
        dependencias.get_current_user
    )
):
    """
    Lista todos los horarios que ha creado el usuario autenticado.

    Args:
        db (Session): Sesion de base de datos.
        current_user (UserResponse): Usuario logueado.

    Returns:
        List[HorarioResponse]: Lista de horarios del usuario.
    """
    return crud.get_my_horarios(db=db, user_id=current_user.id)


@router.delete("/{horario_id}")
def borrar_horario(
    horario_id: int,
    db: Session = Depends(get_db),
    current_user: user_schemas.UserResponse = Depends(
        dependencias.get_current_user
    )
):
    """
    Elimina un horario especifico si pertenece al usuario.

    Args:
        horario_id (int): ID del horario a eliminar.
        db (Session): Sesion de base de datos.
        current_user (UserResponse): Usuario autenticado.

    Returns:
        dict: Mensaje de confirmacion.

    Raises:
        HTTPException (404): Si el horario no existe o no pertenece al usuario.
    """
    exito = crud.delete_horario(
        db=db,
        horario_id=horario_id,
        user_id=current_user.id
    )

    if not exito:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Horario no encontrado o no te pertenece"
        )

    return {"mensaje": "Horario eliminado correctamente"}
