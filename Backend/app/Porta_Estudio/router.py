import os
import uuid
from typing import List

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)
from fastapi.responses import FileResponse
from pypdf import PdfReader
from sqlalchemy.orm import Session

from app import dependencias
from app.Creacion_mats_prof import crud as crud_catalogos
from app.database import get_db
from app.Porta_Estudio import crud, esquemas, modelos
from app.Usuarios import esquemas as user_schemas

router = APIRouter()

# 🔥 CORRECCIÓN DE RUTA: Forzamos la ruta al volumen de Koyeb
# Usamos /workspace porque es el estándar de Buildpacks en Koyeb
UPLOAD_DIR = "/workspace/uploads"

# Intentar crear el directorio si no existe (el volumen debería manejarlo)
if not os.path.exists(UPLOAD_DIR):
    try:
        os.makedirs(UPLOAD_DIR, exist_ok=True)
    except Exception as e:
        print(f"Error creando UPLOAD_DIR: {e}")

@router.post("/", response_model=esquemas.ResourceResponse)
async def subir_recurso(
    title: str = Form(...),
    description: str = Form(None),
    materia_nombre: str = Form(...),
    type: str = Form(...),
    file: UploadFile = File(None),
    url_externa: str = Form(None),
    db: Session = Depends(get_db),
    current_user: user_schemas.UserResponse = Depends(dependencias.get_current_user)
):
    materia_db = crud_catalogos.get_materia_by_name(db, materia_nombre)
    if not materia_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No encontré la materia '{materia_nombre}'."
        )

    path_final = ""
    texto_extraido = None

    if file:
        filename = f"{uuid.uuid4()}-{file.filename}"
        # Guardamos usando la ruta absoluta del volumen
        file_location = os.path.join(UPLOAD_DIR, filename)

        contents = await file.read()
        with open(file_location, "wb") as f:
            f.write(contents)

        # 🚩 IMPORTANTE: Guardamos la ruta ABSOLUTA en la base de datos
        # para que al descargar no haya dudas de dónde está el archivo
        path_final = file_location

        if type == modelos.ResourceType.PDF.value:
            try:
                reader = PdfReader(file_location)
                texto_completo = "".join([page.extract_text() or "" for page in reader.pages])
                texto_extraido = texto_completo[:60000]
            except Exception as e:
                print(f"Error leyendo PDF: {e}")

    elif url_externa:
        path_final = url_externa
        if type == modelos.ResourceType.VIDEO.value:
            texto_extraido = "Video educativo externo."
    else:
        raise HTTPException(status_code=400, detail="Falta archivo o URL.")

    return crud.create_resource_manual(
        db=db, title=title, description=description, type=type,
        path=path_final, materia_id=materia_db.id,
        user_id=current_user.id, content_text=texto_extraido
    )

@router.get("/download/{resource_id}")
def download_resource(resource_id: int, db: Session = Depends(get_db)):
    recurso = db.query(modelos.Resource).filter(modelos.Resource.id == resource_id).first()

    if not recurso:
        raise HTTPException(status_code=404, detail="Recurso no encontrado")

    if recurso.type == modelos.ResourceType.LINK:
        return {"url": recurso.url_or_path, "is_link": True}

    # El file_path ya es absoluto gracias a la corrección en el POST
    file_path = recurso.url_or_path

    if not os.path.exists(file_path):
        # 🔍 DEBUG: Imprimimos en logs para ver qué falló
        print(f"ERROR: Archivo no hallado en {file_path}")
        print(f"Contenido de {UPLOAD_DIR}: {os.listdir(UPLOAD_DIR) if os.path.exists(UPLOAD_DIR) else 'No existe'}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El archivo físico no existe en la ruta registrada."
        )

    nombre_descarga = file_path.split("-", 1)[-1] if "-" in file_path else "archivo"
    
    return FileResponse(
        file_path,
        media_type="application/octet-stream",
        filename=nombre_descarga
    )


@router.get(
    "/buscar_por_nombre/",
    response_model=List[esquemas.ResourceResponse]
)
def buscar_recursos_por_materia(
    nombre: str,
    db: Session = Depends(get_db)
):
    """
    Busca recursos asociados a una materia dada su nombre.

    Utiliza la búsqueda de materias existente para resolver el ID
    y luego filtra los recursos.

    Args:
        nombre (str): Nombre de la materia.
        db (Session): Sesión de base de datos.

    Returns:
        List[ResourceResponse]: Lista de recursos encontrados.
    """
    materia_db = crud_catalogos.get_materia_by_name(db, nombre)
    if not materia_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Materia '{nombre}' no encontrada."
        )

    return crud.get_resources_by_materia(db, materia_id=materia_db.id)

@router.delete("/debug/limpiar_todo")
def limpiar_base_de_datos(db: Session = Depends(get_db)):
    """
    ⚠️ PELIGRO: Borra TODOS los recursos de la base de datos.
    Úsalo solo para limpiar datos viejos con rutas rotas.
    """
    try:
        num_borrados = db.query(modelos.Resource).delete()
        db.commit()
        return {"mensaje": f"Limpieza completada. Se eliminaron {num_borrados} recursos."}
    except Exception as e:
        db.rollback()
        return {"error": f"No se pudo limpiar: {str(e)}"}