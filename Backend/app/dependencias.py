from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app import auth
from app.database import get_db
from app.Usuarios import crud, modelos


# 1. Definimos el esquema de seguridad
# auto_error=False permite que el token sea opcional en la definicion de la ruta,
# facilitando endpoints hibridos (invitados/usuarios).
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/users/login",
    auto_error=False
)


# --- FUNCION AUXILIAR (LOGICA INTERNA) ---

def _decode_token_user(token: str, db: Session):
    """
    Intenta decodificar el token JWT y recuperar el usuario asociado.

    Esta funcion no lanza excepciones HTTP, simplemente retorna None
    si el token es invalido o el usuario no existe, delegando el manejo
    de errores a la dependencia que la invoque.

    Args:
        token (str): El string del token JWT.
        db (Session): Sesion de base de datos.

    Returns:
        User | None: El objeto usuario si es valido, None en caso contrario.
    """
    try:
        payload = jwt.decode(
            token,
            auth.SECRET_KEY,
            algorithms=[auth.ALGORITHM]
        )
        email: str = payload.get("sub")
        if email is None:
            return None
    except JWTError:
        return None

    return crud.get_user_by_email(db, email=email)


# ==========================================
# 2. DEPENDENCIA: USUARIO LOGUEADO (ESTRICTO)
# ==========================================

def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Dependencia estricta que obliga a que el usuario este autenticado.

    Util para rutas protegidas como: Cambiar contraseña, Crear Reseñas,
    Ver Horarios privados, etc.

    Args:
        token (str): Token JWT extraido del header Authorization.
        db (Session): Sesion de base de datos.

    Returns:
        User: El objeto usuario autenticado.

    Raises:
        HTTPException (401): Si no hay token, esta expirado o es invalido.
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autenticado (Falta Token)",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = _decode_token_user(token, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalido o usuario no encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


# ==========================================
# 3. DEPENDENCIA: USUARIO OPCIONAL (INVITADO)
# ==========================================

def get_current_user_optional(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Dependencia flexible que permite acceso a invitados y usuarios logueados.

    Si el token es valido, devuelve el usuario.
    Si no hay token o es invalido, devuelve None (se trata como Invitado).

    Util para: Chatbot (historial opcional), Ver Recursos Publicos.

    Args:
        token (str, optional): Token JWT.
        db (Session): Sesion de base de datos.

    Returns:
        User | None: El usuario o None.
    """
    if not token:
        return None  # Modo Invitado

    user = _decode_token_user(token, db)
    if not user:
        return None  # Si el token expiro, lo tratamos como invitado

    return user


# ==========================================
# 4. DEPENDENCIA: SOLO ADMINISTRADOR
# ==========================================

def require_admin(current_user: modelos.User = Depends(get_current_user)):
    """
    Verifica que el usuario autenticado tenga permisos de administrador.

    Util para: Subir analisis de WhatsApp, Borrar usuarios, Gestion avanzada.

    Args:
        current_user (User): Usuario inyectado por get_current_user.

    Returns:
        User: El mismo usuario si es admin.

    Raises:
        HTTPException (403): Si el usuario no tiene rol de admin.
    """
    # Se utiliza getattr para evitar errores si la columna 'role' aun no
    # existe en la base de datos (migracion pendiente), asumiendo 'student'
    # por defecto.
    role = getattr(current_user, "role", "student")

    if role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado: Se requieren permisos de Administrador"
        )
    return current_user
