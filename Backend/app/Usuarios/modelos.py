from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    """
    Modelo de Base de Datos para los Usuarios del sistema.

    Representa a los estudiantes o administradores registrados en la
    plataforma. Gestiona la autenticación y la relación con otras
    entidades como horarios.

    Atributos:
        id (int): Identificador único del usuario.
        email (str): Correo electrónico (único).
        full_name (str): Nombre completo del alumno.
        career (str): Carrera académica (ej. ISC, IA, LCD).
        hashed_password (str): Contraseña encriptada (hash).
        is_active (bool): Estado de la cuenta (activa/inactiva).
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    career = Column(String(100), nullable=False)

    # Se usa String(255) para asegurar espacio suficiente para el hash
    hashed_password = Column(String(255), nullable=False)

    is_active = Column(Boolean, default=True)

    role = Column(String(20), default="student", nullable=False)

    # Relación uno-a-muchos con Horarios.
    # Se utiliza la ruta completa del modelo para evitar
    # importaciones circulares.
    horarios = relationship(
        "app.Horarios.modelos.Horario",
        back_populates="usuario"
    )
