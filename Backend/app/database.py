import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()

# --- CAMBIO IMPORTANTE AQUÍ ---
# 1. Intentamos obtener la URL completa (Ideal para Render/Aiven)
database_url = os.getenv("DATABASE_URL")

# 2. Si no existe (estamos en local), la construimos por partes
if not database_url:
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_NAME = os.getenv("DB_NAME")
    
    database_url = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

# 3. FIX PARA AIVEN: Aiven da la url como "mysql://", pero SQLAlchemy necesita "mysql+pymysql://"
if database_url and database_url.startswith("mysql://"):
    database_url = database_url.replace("mysql://", "mysql+pymysql://")

# 4. Crear el motor
# pool_recycle: Es vital para MySQL en la nube para evitar desconexiones por inactividad
engine = create_engine(
    database_url, 
    pool_recycle=3600,
    pool_pre_ping=True 
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()