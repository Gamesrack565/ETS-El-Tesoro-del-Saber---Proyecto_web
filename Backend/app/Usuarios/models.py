from sqlalchemy import Column, Integer, String, Boolean
from app.database import Base

class User(Base):
    __tablename__ = "users" # Nombre de la tabla en MySQL

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=False) # Nombre del alumno
    career = Column(String(100), nullable=False)    # Carrera (ISC, IA, LCD)
    hashed_password = Column(String(255), nullable=False) # Contraseña encriptada
    is_active = Column(Boolean, default=True)