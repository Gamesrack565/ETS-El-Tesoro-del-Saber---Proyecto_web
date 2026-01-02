import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.Analisis_IA import router as ai_router
from app.Chatbot import router as chatbot_router
from app.Creacion_mats_prof import router as catalogos_router
from app.database import Base, engine
from app.Estadistica import router as stats_router
from app.Horarios import router as horarios_router
from app.Porta_Estudio import router as study_router
from app.Reviews import router as reviews_router
from app.Usuarios import router as user_router

# 1. Crear Tablas en la Base de Datos
# Esto genera las tablas si no existen al iniciar la aplicación.
Base.metadata.create_all(bind=engine)

# Configuración de la aplicación FastAPI
app = FastAPI(
    title="El Tesoro del Saber (ETS) - Backend",
    version="1.0.0",
    description=(
        "Backend unificado para Chatbot, Reseñas, Horarios y Recursos."
    )
)

# 2. CONFIGURACION DE CORS (CRITICO)
# Define los orígenes permitidos para evitar bloqueos por políticas del navegador
# al comunicar el Frontend (React/Vite) con el Backend.
# 2. CONFIGURACION DE CORS (ACTUALIZADA)
origins = [
    os.getenv("FRONTEND_URL"),      # Esto leerá tu link de Vercel desde Koyeb
    "http://localhost:5173",        # Para que sigas probando en tu PC
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,        # Dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],          # Permitir todos los métodos (GET, POST...)
    allow_headers=["*"],          # Permitir todos los headers (Tokens, etc.)
)

# 3. Configuración de Archivos Estáticos (Uploads)
# Se asegura de que la carpeta exista para evitar errores al montar la ruta.
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Monta la carpeta para que los archivos sean accesibles vía URL
app.mount(
    "/uploads",
    StaticFiles(directory=UPLOAD_DIR),
    name="uploads"
)

# 4. Registro de Rutas (Endpoints)
# Se incluyen los routers de cada módulo con un prefijo estandarizado.

app.include_router(
    user_router.router,
    prefix="/api/users",
    tags=["Usuarios"]
)
app.include_router(
    catalogos_router.router,
    prefix="/api/catalogos",
    tags=["Catálogos (Profes y Materias)"]
)
app.include_router(
    reviews_router.router,
    prefix="/api/reviews",
    tags=["Reseñas"]
)
app.include_router(
    study_router.router,
    prefix="/api/portal",
    tags=["Portal de Estudio"]
)
app.include_router(
    horarios_router.router,
    prefix="/api/horarios",
    tags=["Horarios"]
)
app.include_router(
    chatbot_router.router,
    prefix="/api/bot",
    tags=["Chatbot IA"]
)
app.include_router(
    ai_router.router,
    prefix="/api/ia",
    tags=["Análisis WhatsApp"]
)
app.include_router(
    stats_router.router,
    prefix="/api/stats",
    tags=["Dashboard Estadísticas"]
)


@app.get("/")
def read_root():
    """
    Endpoint raíz para verificar el estado de la API.

    Returns:
        dict: Mensaje de confirmación de funcionamiento.
    """
    return {"message": "API del Portal ESCOM funcionando al 100%"}
