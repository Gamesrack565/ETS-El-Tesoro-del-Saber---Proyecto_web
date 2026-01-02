from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base
from app.Usuarios.models import User # 1. Importamos la clase User real

class Profesor(Base):
    __tablename__ = "profesores"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(150), unique=True, index=True, nullable=False)
    resenas = relationship("Resena", back_populates="profesor")

class Materia(Base):
    __tablename__ = "materias"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(150), unique=True, index=True, nullable=False)
    resenas = relationship("Resena", back_populates="materia")

class Resena(Base):
    __tablename__ = "resenas"
    id = Column(Integer, primary_key=True, index=True)
    
    comentario = Column(Text, nullable=True)
    calificacion = Column(Float, nullable=False)
    dificultad = Column(Integer, nullable=False)
    
    profesor_id = Column(Integer, ForeignKey("profesores.id"))
    materia_id = Column(Integer, ForeignKey("materias.id"))
    user_id = Column(Integer, ForeignKey("users.id"))

    profesor = relationship("Profesor", back_populates="resenas")
    materia = relationship("Materia", back_populates="resenas")
    usuario = relationship(User) # 2. Usamos la clase directamente, sin comillas