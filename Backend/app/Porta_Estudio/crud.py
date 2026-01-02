from typing import Optional

from sqlalchemy.orm import Session

from app.Porta_Estudio import modelos


def get_resources_by_materia(db: Session, materia_id: int):
    """
    Obtiene todos los recursos asociados a una materia específica.

    Args:
        db (Session): Sesión de la base de datos.
        materia_id (int): ID de la materia a consultar.

    Returns:
        List[Resource]: Lista de objetos Resource encontrados.
    """
    return db.query(modelos.Resource).filter(
        modelos.Resource.materia_id == materia_id
    ).all()


def create_resource_manual(
    db: Session,
    title: str,
    description: str,
    type: str,
    path: str,
    materia_id: int,
    user_id: int,
    content_text: Optional[str] = None
):
    """
    Crea un nuevo recurso manualmente en la base de datos.

    Esta función es ideal para registrar recursos provenientes de archivos
    subidos, donde la ruta (path) se genera en el backend.

    Args:
        db (Session): Sesión de la base de datos.
        title (str): Título del recurso.
        description (str): Descripción breve del contenido.
        type (str): Tipo de recurso ('pdf', 'video', 'link', etc.).
                    SQLAlchemy mapeará este string al Enum correspondiente.
        path (str): URL o ruta del archivo en el sistema de archivos.
        materia_id (int): ID de la materia a la que pertenece.
        user_id (int): ID del usuario que subió el recurso.
        content_text (Optional[str]): Texto extraído del contenido (OCR/PDF)
                                      para alimentar el contexto de la IA.

    Returns:
        Resource: El objeto recurso creado y persistido.
    """
    db_resource = modelos.Resource(
        title=title,
        description=description,
        type=type,
        url_or_path=path,
        materia_id=materia_id,
        user_id=user_id,
        content_text=content_text
    )

    db.add(db_resource)
    db.commit()
    db.refresh(db_resource)
    return db_resource
