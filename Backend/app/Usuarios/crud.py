from sqlalchemy.orm import Session

from app import auth
from app.Usuarios import esquemas, modelos


def get_user_by_email(db: Session, email: str):
    """
    Busca un usuario en la base de datos por su correo electrónico.

    Args:
        db (Session): Sesión de la base de datos.
        email (str): Correo electrónico a buscar.

    Returns:
        User | None: El objeto usuario si existe, None en caso contrario.
    """
    return db.query(modelos.User).filter(modelos.User.email == email).first()


def create_user(db: Session, user: esquemas.UserCreate):
    """
    Registra un nuevo usuario en la base de datos.

    Se encarga de hashear la contraseña antes de persistirla
    para garantizar la seguridad.

    Args:
        db (Session): Sesión de la base de datos.
        user (UserCreate): Esquema con los datos del nuevo usuario.

    Returns:
        User: El objeto usuario creado.
    """
    # Usamos la utilidad de auth para encriptar la contraseña plana
    hashed_password = auth.get_password_hash(user.password)

    db_user = modelos.User(
        email=user.email,
        hashed_password=hashed_password,  # Guardamos solo el hash
        full_name=user.full_name,
        career=user.career
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_password(db: Session, user_id: int, new_password_hash: str):
    """
    Actualiza la contraseña de un usuario específico.

    Args:
        db (Session): Sesión de la base de datos.
        user_id (int): ID del usuario a modificar.
        new_password_hash (str): Nueva contraseña ya encriptada.

    Returns:
        User | None: El objeto usuario actualizado o None si no existe.
    """
    db_user = db.query(modelos.User).filter(modelos.User.id == user_id).first()

    if db_user:
        db_user.hashed_password = new_password_hash
        db.commit()
        db.refresh(db_user)

    return db_user
