from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Horario(Base):
    """
    Modelo de Base de Datos para la cabecera de un Horario.

    Agrupa un conjunto de materias seleccionadas por un usuario.
    Funciona como un contenedor para los items del horario.

    Atributos:
        id (int): Identificador unico del horario.
        nombre (str): Nombre personalizado dado por el usuario.
        user_id (int): Clave foranea que vincula al usuario creador.
    """
    __tablename__ = "horarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))

    # Relacion con el Usuario propietario.
    # Se usa la ruta completa para evitar importaciones circulares.
    usuario = relationship(
        "app.Usuarios.modelos.User",
        back_populates="horarios"
    )

    # Relacion uno-a-muchos con los items del horario.
    # cascade="all, delete-orphan": Si se borra el horario,
    # se borran sus items.
    items = relationship(
        "ItemHorario",
        back_populates="horario",
        cascade="all, delete-orphan"
    )


class ItemHorario(Base):
    """
    Modelo de Base de Datos para un elemento individual del horario.

    Representa una materia especifica asignada a un horario, incluyendo
    informacion sobre la hora o grupo seleccionado.

    Atributos:
        id (int): Identificador unico del item.
        horario_id (int): Clave foranea al horario padre.
        materia_id (int): Clave foranea a la materia del catalogo.
        hora_grupo (str): Texto descriptivo del horario (ej. "7:00 - 8:30").
    """
    __tablename__ = "items_horario"

    id = Column(Integer, primary_key=True, index=True)
    horario_id = Column(Integer, ForeignKey("horarios.id"))
    materia_id = Column(Integer, ForeignKey("materias.id"))
    hora_grupo = Column(String(50), nullable=True)

    # Relacion inversa con Horario
    horario = relationship("Horario", back_populates="items")

    # Relacion con la Materia para obtener su nombre y detalles.
    materia = relationship("app.Creacion_mats_prof.modelos.Materia")

    # Propiedad virtual (no existe en la tabla SQL).
    # Pydantic (orm_mode/from_attributes) usara esto para llenar el campo
    # 'materia_nombre' en la respuesta JSON sin necesidad de queries complejas.
    @property
    def materia_nombre(self):
        """Devuelve el nombre de la materia asociada si existe."""
        return self.materia.nombre if self.materia else None
