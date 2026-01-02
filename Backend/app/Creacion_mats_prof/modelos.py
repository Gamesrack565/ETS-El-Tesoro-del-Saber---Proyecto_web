from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Profesor(Base):
    """
    Modelo de Base de Datos para la entidad Profesor.

    Representa a los docentes registrados en el sistema sobre los cuales
    los alumnos pueden escribir reseñas.

    Atributos:
        id (int): Identificador unico del profesor.
        nombre (str): Nombre completo del profesor (unico).
    """
    __tablename__ = "profesores"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(150), unique=True, index=True, nullable=False)

    # Relacion uno-a-muchos con Resena.
    # Se utiliza string para 'Resena' para evitar importaciones circulares.
    resenas = relationship(
        "app.Reviews.modelos.Resena",
        back_populates="profesor"
    )


class Materia(Base):
    """
    Modelo de Base de Datos para la entidad Materia (Asignatura).

    Representa las clases o cursos disponibles en la escuela. Actua como
    punto central para reseñas, recursos de estudio y horarios.

    Atributos:
        id (int): Identificador unico de la materia.
        nombre (str): Nombre oficial de la materia (unico).
    """
    __tablename__ = "materias"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(150), unique=True, index=True, nullable=False)

    # 1. Relacion con Reseñas (Reviews)
    # Permite acceder a todas las opiniones dejadas sobre esta materia.
    resenas = relationship(
        "app.Reviews.modelos.Resena",
        back_populates="materia"
    )

    # 2. Relacion con Portal de Estudio (Resources)
    # Conecta la materia con sus archivos PDF, videos o enlaces asociados.
    resources = relationship(
        "app.Porta_Estudio.modelos.Resource",
        back_populates="materia"
    )

    # 3. Relacion con Horarios (ItemsHorario)
    # Permite vincular la materia a bloques especificos en el calendario.
    items_horario = relationship(
        "app.Horarios.modelos.ItemHorario",
        back_populates="materia"
    )
