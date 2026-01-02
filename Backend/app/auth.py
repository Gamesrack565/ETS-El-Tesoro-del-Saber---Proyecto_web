import os # <--- Agrega esto
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt
from passlib.context import CryptContext
from dotenv import load_dotenv # <--- Agrega esto

load_dotenv() # <--- Agrega esto

# --- CONFIGURACION ---
# Leemos del entorno, si no existe (local), usa la clave por defecto
SECRET_KEY = os.getenv("SECRET_KEY", "esta_es_una_clave_super_secreta_cambiala")
ALGORITHM = "HS256"
# Leemos del entorno, por defecto 1 semana (10080 min)
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 10080))


# --- FUNCIONES ---

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Compara una contraseña en texto plano con su hash almacenado en la BD.

    Args:
        plain_password (str): La contraseña introducida por el usuario.
        hashed_password (str): El hash guardado en la base de datos.

    Returns:
        bool: True si coinciden, False en caso contrario.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Genera un hash seguro para una contraseña utilizando el esquema configurado

    Args:
        password (str): La contraseña en texto plano.

    Returns:
        str: El hash de la contraseña.
    """
    return pwd_context.hash(password)


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Crea un Token JWT (JSON Web Token) con tiempo de expiración.

    Permite definir un tiempo de expiración personalizado (útil para
    tokens de recuperación de contraseña) o usar el valor por defecto.

    Args:
        data (dict): Datos (payload) a incluir en el token.
        expires_delta (Optional[timedelta]): Tiempo de vida del token.
                                             Si es None, usa el default.

    Returns:
        str: El token JWT codificado.
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
