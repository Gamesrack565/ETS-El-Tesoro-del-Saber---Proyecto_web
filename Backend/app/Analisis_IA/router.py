from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session
from app import dependencias
from app.Analisis_IA import analyzer, parser
from app.Creacion_mats_prof import crud as crud_catalogos
from app.Creacion_mats_prof import esquemas as esquemas_catalogos
from app.database import get_db
from app.Reviews import crud as crud_reviews
from app.Reviews import esquemas as esquemas_reviews
from app.Usuarios import esquemas as user_schemas

router = APIRouter()


@router.post("/process_reviews")
async def process_reviews_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin_user: user_schemas.UserResponse = Depends(dependencias.require_admin)
):
    """
    Procesa un archivo de historial de chat para extraer y guardar reseñas.

    Flujo principal:
    1. Valida y lee el archivo de texto.
    2. Parsea el chat (limpieza y estructuración).
    3. Analiza el contenido con IA para extraer reseñas.
    4. Verifica o crea la materia 'General'.
    5. Verifica o crea los profesores mencionados.
    6. Guarda las reseñas en la base de datos.

    Args:
        file (UploadFile): Archivo .txt con el historial de chat.
        db (Session): Sesión de base de datos.
        admin_user (UserResponse): Usuario administrador autenticado.

    Returns:
        dict: Resumen del proceso indicando éxito, mensaje y datos procesados.

    Raises:
        HTTPException: Si el archivo no es .txt o no se puede decodificar.
    """
    # 1. Validar extensión del archivo
    if not file.filename.endswith('.txt'):
        raise HTTPException(
            status_code=400,
            detail="Solo se aceptan archivos .txt"
        )

    # 2. Leer contenido con manejo de errores de encoding
    # Se intentan varias codificaciones comunes para evitar errores
    # al leer archivos generados en diferentes sistemas operativos (Win/Mac).
    content_bytes = await file.read()
    content_str = ""
    for encoding in ['utf-8', 'latin-1', 'cp1252']:
        try:
            content_str = content_bytes.decode(encoding)
            break
        except UnicodeDecodeError:
            continue

    if not content_str:
        raise HTTPException(
            status_code=400,
            detail="No se pudo leer el archivo (encoding desconocido)."
        )

    # 3. Parsear (Limpieza y estructuración de mensajes)
    clean_messages = parser.parse_whatsapp_chat(content_str)
    print(
        f"--- Chat cargado por Admin {admin_user.email}: "
        f"{len(clean_messages)} mensajes ---"
    )

    if not clean_messages:
        return {
            "success": False,
            "message": "El archivo no contiene mensajes validos."
        }

    # 4. Analizar con IA
    extracted_reviews = analyzer.analyze_reviews(clean_messages)

    if not extracted_reviews:
        return {
            "success": True,
            "message": "La IA analizo el chat pero no encontro reseñas.",
            "data": []
        }

    saved_reviews = []
    profesores_nuevos = 0

    # ID de usuario sistema para atribuir la creación de la reseña
    # Se usa un ID fijo (1) o el del admin actual.
    system_user_id = 1

    print("--- Guardando en Base de Datos ---")

    # --- GESTION DE MATERIA ---
    # Se busca una materia genérica "General" para asignar las reseñas
    # extraídas del chat, ya que el chat no especifica la materia exacta.
    materia_generica_nombre = "General"
    materia_db = crud_catalogos.get_materia_by_name(
        db, materia_generica_nombre
    )

    if not materia_db:
        print(f"Creando materia automatica '{materia_generica_nombre}'...")
        nueva_mat = esquemas_catalogos.MateriaCreate(
            nombre=materia_generica_nombre
        )
        materia_db = crud_catalogos.create_materia(db, nueva_mat)

    materia_id_final = materia_db.id

    # Iteración sobre las reseñas extraídas para guardarlas
    for review_data in extracted_reviews:
        nombre_profe = review_data['profesor_nombre']

        # A. Gestión del Profesor
        # Verifica si existe; si no, lo crea automáticamente.
        db_profesor = crud_catalogos.get_profesor_by_name(
            db, nombre=nombre_profe
        )

        if not db_profesor:
            print(f"Nuevo profesor detectado: {nombre_profe}")
            nuevo_profe_schema = esquemas_catalogos.ProfesorCreate(
                nombre=nombre_profe
            )
            db_profesor = crud_catalogos.create_profesor(
                db=db, profesor=nuevo_profe_schema
            )
            profesores_nuevos += 1

        real_profesor_id = db_profesor.id

        # B. Creación de la Reseña
        # Se anexa la fuente original al comentario para trazabilidad.
        fuente = review_data['autor_original']
        texto_final = (
            f"{review_data['comentario']}\n"
            f"(Fuente: Chat WhatsApp - {fuente})"
        )

        # Normalización y seguridad de la calificación
        try:
            calif_final = float(review_data.get('calificacion', 5))
            if calif_final > 10:
                calif_final = 10.0
        except (ValueError, TypeError):
            calif_final = 5.0

        # Normalización de la dificultad
        try:
            dificultad_val = int(review_data.get('dificultad', 5))
        except (ValueError, TypeError):
            dificultad_val = 5

        nueva_resena = esquemas_reviews.ResenaCreate(
            profesor_id=real_profesor_id,
            materia_nombre=materia_generica_nombre,
            comentario=texto_final,
            calificacion=calif_final,
            dificultad=dificultad_val
        )

        try:
            saved = crud_reviews.create_resena(
                db=db,
                resena=nueva_resena,
                materia_id=materia_id_final,
                user_id=system_user_id
            )
            saved_reviews.append(saved)
        except Exception as e:
            print(f"Error guardando reseña: {e}")

    return {
        "success": True,
        "message": (
            f"Se procesaron {len(extracted_reviews)} reseñas. "
            f"{profesores_nuevos} profesores nuevos creados."
        ),
        "data": extracted_reviews
    }
