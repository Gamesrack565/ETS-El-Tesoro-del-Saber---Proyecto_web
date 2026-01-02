from pydantic import BaseModel


# --- ESQUEMAS DE PROFESORES ---

class ProfesorBase(BaseModel):
    """
    Esquema base para la entidad Profesor.

    Contiene los atributos comunes requeridos tanto para la creacion
    como para la lectura de un profesor.

    Atributos:
        nombre (str): El nombre completo del profesor.
    """
    nombre: str


class ProfesorCreate(ProfesorBase):
    """
    Esquema para la creacion de un nuevo Profesor.

    Hereda de ProfesorBase. No añade campos adicionales por ahora,
    pero permite diferenciar semanticamente la operacion de creacion.
    """
    pass


class Profesor(ProfesorBase):
    """
    Esquema de respuesta para la entidad Profesor (Lectura).

    Incluye el ID generado por la base de datos.

    Atributos:
        id (int): Identificador unico del profesor en la BD.
    """
    id: int

    class Config:
        """
        Configuracion de Pydantic.

        from_attributes = True (antes orm_mode) permite mapear objetos
        ORM de SQLAlchemy directamente a este esquema Pydantic.
        """
        from_attributes = True


# --- ESQUEMAS DE MATERIAS ---

class MateriaBase(BaseModel):
    """
    Esquema base para la entidad Materia.

    Atributos:
        nombre (str): El nombre oficial de la materia.
    """
    nombre: str


class MateriaCreate(MateriaBase):
    """
    Esquema para la creacion de una nueva Materia.

    Se mantiene separado del base para permitir validaciones especificas
    al momento de crear (ej. longitud minima) en el futuro.
    """
    pass


class Materia(MateriaBase):
    """
    Esquema de respuesta para la entidad Materia.

    Atributos:
        id (int): Identificador unico de la materia en la BD.
    """
    id: int

    class Config:
        from_attributes = True
