from pydantic import BaseModel, EmailStr


# --- ESQUEMAS BASICOS DE USUARIO ---

class UserBase(BaseModel):
    """
    Esquema base con los datos comunes del usuario.

    Atributos:
        email (EmailStr): Correo electrónico (validado por Pydantic).
        full_name (str): Nombre completo del usuario.
        career (str): Carrera o profesión asociada.
    """
    email: EmailStr
    full_name: str
    career: str


class UserCreate(UserBase):
    """
    Esquema para el registro de nuevos usuarios.

    Hereda de UserBase e incluye la contraseña en texto plano,
    que será hasheada antes de guardarse en la BD.

    Atributos:
        password (str): Contraseña del usuario.
    """
    password: str


class UserResponse(UserBase):
    """
    Esquema de respuesta pública del usuario.

    Se utiliza para devolver datos al frontend, excluyendo información
    sensible como la contraseña.

    Atributos:
        id (int): Identificador único del usuario.
        is_active (bool): Estado de la cuenta.
    """
    id: int
    is_active: bool

    class Config:
        from_attributes = True


# --- ESQUEMAS DE AUTENTICACION ---

class UserLogin(BaseModel):
    """
    Esquema para las credenciales de inicio de sesión.

    Atributos:
        email (EmailStr): Correo del usuario.
        password (str): Contraseña para verificar.
    """
    email: EmailStr
    password: str


class Token(BaseModel):
    """
    Esquema del token JWT de respuesta.

    Se devuelve al usuario tras un login exitoso.

    Atributos:
        access_token (str): El string del token JWT.
        token_type (str): Tipo de token (generalmente 'bearer').
    """
    access_token: str
    token_type: str


# --- ESQUEMAS DE GESTION DE CONTRASEÑAS ---

class UserChangePassword(BaseModel):
    """
    Esquema para cambiar la contraseña estando autenticado.

    Atributos:
        current_password (str): Contraseña actual para validación.
        new_password (str): Nueva contraseña deseada.
    """
    current_password: str
    new_password: str


class UserRequestReset(BaseModel):
    """
    Esquema para solicitar la recuperación de contraseña.

    Atributos:
        email (EmailStr): Correo donde se enviará el enlace de recuperación.
    """
    email: EmailStr


class UserResetPassword(BaseModel):
    """
    Esquema para establecer una nueva contraseña mediante recuperación.

    Atributos:
        token (str): Token de seguridad enviado por correo.
        new_password (str): La nueva contraseña a establecer.
    """
    token: str
    new_password: str
