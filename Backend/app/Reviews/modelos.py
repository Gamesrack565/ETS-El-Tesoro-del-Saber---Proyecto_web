from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship

from app.database import Base
from app.Usuarios.modelos import User


class Resena(Base):
    """
    Modelo de Base de Datos para las Reseñas.

    Almacena la opinión, calificación y nivel de dificultad que un usuario
    asigna a un profesor en una materia específica.

    Atributos:
        id (int): Identificador único de la reseña.
        comentario (str): Texto explicativo de la experiencia.
        calificacion (float): Puntuación numérica (ej. 0.0 a 10.0).
        dificultad (int): Nivel de dificultad (ej. 1 a 5).
        profesor_id (int): Clave foránea del profesor evaluado.
        materia_id (int): Clave foránea de la materia cursada.
        user_id (int): Clave foránea del usuario autor.
    """
    __tablename__ = "resenas"

    id = Column(Integer, primary_key=True, index=True)

    comentario = Column(Text, nullable=True)
    calificacion = Column(Float, nullable=False)
    dificultad = Column(Integer, nullable=False)

    profesor_id = Column(Integer, ForeignKey("profesores.id"))
    materia_id = Column(Integer, ForeignKey("materias.id"))
    user_id = Column(Integer, ForeignKey("users.id"))

    # Relaciones con otras entidades
    # Se usan cadenas para evitar importaciones circulares en tiempo de carga
    profesor = relationship(
        "app.Creacion_mats_prof.modelos.Profesor",
        back_populates="resenas"
    )

    materia = relationship(
        "app.Creacion_mats_prof.modelos.Materia",
        back_populates="resenas"
    )

    usuario = relationship(User)

    votos = relationship("Voto", back_populates="resena")

    @property
    def total_votos_utiles(self):
        """
        Calcula dinámicamente el total de votos marcados como 'útiles'.

        Itera sobre la relación 'votos' cargada en memoria.
        Nota: Esto puede impactar el rendimiento si hay muchos votos
        y no se usa eager loading.
        """
        return sum(1 for voto in self.votos if voto.es_util)


class Voto(Base):
    """
    Modelo de Base de Datos para los Votos de utilidad.

    Permite a los usuarios marcar si una reseña les resultó útil o no.

    Atributos:
        id (int): Identificador único del voto.
        user_id (int): Usuario que emite el voto.
        resena_id (int): Reseña votada.
        es_util (bool): True indica 'Útil' (Like), False indica 'No útil'.
    """
    __tablename__ = "votos"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    resena_id = Column(Integer, ForeignKey("resenas.id"))
    es_util = Column(Boolean, nullable=False)

    usuario = relationship(User)
    resena = relationship("Resena", back_populates="votos")
