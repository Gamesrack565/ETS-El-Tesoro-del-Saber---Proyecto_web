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

# Directorio de almacenamiento local
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/", response_model=esquemas.ResourceResponse)
async def subir_recurso(
    title: str = Form(...),
    description: str = Form(None),
    materia_nombre: str = Form(...),
    type: str = Form(...),
    file: UploadFile = File(None),
    url_externa: str = Form(None),
    db: Session = Depends(get_db),
    current_user: user_schemas.UserResponse = Depends(
        dependencias.get_current_user
    )
):
    """
    Sube un recurso de estudio (PDF, Video o Enlace) al sistema.

    Realiza las siguientes acciones:
    1. Busca la materia especificada (incluyendo búsqueda difusa).
    2. Guarda el archivo físicamente o procesa la URL externa.
    3. Si es un PDF, extrae el texto contenido para alimentar a la IA.
    4. Registra los metadatos en la base de datos.

    Args:
        title (str): Título del recurso.
        description (str, optional): Descripción breve.
        materia_nombre (str): Nombre de la materia para buscar su ID.
        type (str): Tipo de recurso ('pdf', 'video', 'link', 'image').
        file (UploadFile, optional): Archivo binario si se sube desde el PC.
        url_externa (str, optional): Enlace si es un recurso web.
        db (Session): Sesión de base de datos.
        current_user (UserResponse): Usuario autenticado.

    Returns:
        ResourceResponse: El objeto recurso creado.

    Raises:
        HTTPException (404): Si la materia no existe.
        HTTPException (400): Si no se envía ni archivo ni URL.
    """
    # 1. BUSCADOR INTELIGENTE DE MATERIA
    # Utilizamos el CRUD de catálogos que soporta búsqueda difusa (fuzzy match)
    materia_db = crud_catalogos.get_materia_by_name(db, materia_nombre)

    if not materia_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(f"No encontre la materia '{materia_nombre}'. "
                    f"Verifica el nombre.")
        )

    real_materia_id = materia_db.id

    # 2. PROCESAMIENTO DEL ARCHIVO O URL
    path_final = ""
    texto_extraido = None

    # CASO A: Archivo físico subido
    if file:
        # Generar nombre único con UUID para evitar colisiones de nombres
        filename = f"{uuid.uuid4()}-{file.filename}"
        file_location = os.path.join(UPLOAD_DIR, filename)

        # Leer contenido y guardar en disco
        # Nota: Para archivos muy grandes, considerar usar chunks (shutil).
        contents = await file.read()
        with open(file_location, "wb") as f:
            f.write(contents)

        # Guardamos la ruta relativa para la base de datos
        path_final = f"uploads/{filename}"

        # --- EXTRACCION DE TEXTO (SOLO PDF) ---
        # Validamos si el tipo declarado coincide con el enum de PDF
        if type == modelos.ResourceType.PDF.value:
            try:
                print(f"Analizando PDF: {filename}...")
                reader = PdfReader(file_location)
                texto_completo = ""

                # Iteramos sobre todas las páginas para extraer texto
                for page in reader.pages:
                    extracted = page.extract_text()
                    if extracted:
                        texto_completo += extracted + "\n"

                # Limitamos la longitud para no saturar la columna de la BD
                # MySQL LONGTEXT soporta mucho, pero limitamos por performance.
                texto_extraido = texto_completo[:60000]
                print(
                    f"Texto extraido: {len(texto_extraido)} caracteres."
                )

            except Exception as e:
                # Si falla (PDF encriptado o escaneado sin OCR), no bloqueamos
                # la subida, simplemente no guardamos el texto extraído.
                print(
                    f"Advertencia: Error leyendo PDF "
                    f"(puede estar encriptado o ser imagen): {e}"
                )

    # CASO B: Link Externo
    elif url_externa:
        path_final = url_externa
        if type == modelos.ResourceType.VIDEO.value:
            # Placeholder para que la IA sepa que es un video externo
            texto_extraido = "Video educativo externo."

    else:
        # Si no hay ni archivo ni URL, es un error de solicitud
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debes subir un archivo o proporcionar un link."
        )

    # 3. GUARDADO USANDO EL CRUD
    # Se llama a la función manual para poder pasar el content_text
    return crud.create_resource_manual(
        db=db,
        title=title,
        description=description,
        type=type,
        path=path_final,
        materia_id=real_materia_id,
        user_id=current_user.id,
        content_text=texto_extraido  # Crucial para el contexto del Chatbot
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


@router.get("/download/{resource_id}")
def download_resource(
    resource_id: int,
    db: Session = Depends(get_db)
):
    """
    Permite descargar un archivo físico o redirigir si es un link.

    Args:
        resource_id (int): ID del recurso.
        db (Session): Sesión de base de datos.

    Returns:
        FileResponse | dict: El archivo binario o un objeto JSON con la URL.
    """
    recurso = db.query(modelos.Resource).filter(
        modelos.Resource.id == resource_id
    ).first()

    if not recurso:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recurso no encontrado"
        )

    # Si es un enlace externo, devolvemos la URL para que el frontend redirija
    if recurso.type == modelos.ResourceType.LINK:
        return {"url": recurso.url_or_path, "is_link": True}

    file_path = recurso.url_or_path

    # Seguridad: Evitar Path Traversal verificando existencia
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El archivo fisico no existe en el servidor."
        )

    # Limpieza del nombre para la descarga:
    # Se intenta remover el UUID prefijado (uploads/UUID-nombre.pdf)
    # Si hay un guion, tomamos lo que sigue; si no, nombre genérico.
    if "-" in file_path:
        nombre_descarga = file_path.split("-", 1)[-1]
    else:
        nombre_descarga = "archivo.pdf"

    return FileResponse(
        file_path,
        media_type="application/octet-stream",
        filename=nombre_descarga
    )
