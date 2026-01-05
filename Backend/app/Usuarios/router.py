import os

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app import auth, dependencias
from app.database import get_db
from app.Usuarios import crud, esquemas

# Cargar variables de entorno
load_dotenv()

router = APIRouter()

# ==========================================
# CONFIGURACION DE CORREO (FastAPI-Mail)
# ==========================================
conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_PORT=int(os.getenv("MAIL_PORT", 587)),
    MAIL_SERVER=os.getenv("MAIL_SERVER"),
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)


# ==========================================
# 1. REGISTRO Y AUTENTICACION
# ==========================================

@router.post("/register", response_model=esquemas.UserResponse)
def register_user(user: esquemas.UserCreate, db: Session = Depends(get_db)):
    """
    Registra un nuevo usuario en la plataforma.
    """
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado"
        )
    return crud.create_user(db=db, user=user)


@router.post("/login", response_model=esquemas.Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Autentica a un usuario y genera un token de acceso JWT.
    """
    user = crud.get_user_by_email(db, email=form_data.username)
    if not user or not auth.verify_password(
        form_data.password, user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=esquemas.UserResponse)
def read_users_me(
    current_user: esquemas.UserResponse = Depends(
        dependencias.get_current_user
    )
):
    """Devuelve el perfil del usuario actual."""
    return current_user


# ==========================================
# 2. GESTION DE CONTRASEÑA (Usuario Logueado)
# ==========================================

@router.post("/change-password", status_code=status.HTTP_200_OK)
def change_password(
    datos: esquemas.UserChangePassword,
    db: Session = Depends(get_db),
    current_user: esquemas.UserResponse = Depends(
        dependencias.get_current_user
    )
):
    """Permite cambiar la contraseña estando logueado."""
    user_db = crud.get_user_by_email(db, current_user.email)
    if not auth.verify_password(
        datos.current_password, user_db.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña actual no coincide"
        )

    new_hash = auth.get_password_hash(datos.new_password)
    crud.update_password(db, user_db.id, new_hash)

    return {"message": "Contraseña actualizada correctamente"}


# ==========================================
# 3. RECUPERACION DE CONTRASEÑA (Olvido)
# ==========================================

@router.post("/request-password-reset")
async def request_password_reset(
    datos: esquemas.UserRequestReset,
    db: Session = Depends(get_db)
):
    """
    Paso 1: Solicitar restablecimiento (Enviar correo).
    """
    user = crud.get_user_by_email(db, datos.email)

    if not user:
        return {
            "message": "Si el correo existe, recibirás instrucciones pronto."
        }

    reset_token = auth.create_access_token(
        data={"sub": user.email, "type": "reset"}
    )

    base_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
    link = f"{base_url}/reset-password?token={reset_token}"

    # Construcción meticulosa del HTML para respetar PEP 8 y tu contenido
    html = (
        '<div style="max-width: 600px; margin: 0 auto; '
        'font-family: Arial, sans-serif; border: 1px solid #e0e0e0; '
        'border-radius: 10px; overflow: hidden; '
        'box-shadow: 0 4px 8px rgba(0,0,0,0.05);">'
        '<div style="background-color: #0056b3; color: white;'
        'padding: 20px; text-align: center;">'
        '<h2 style="margin: 0;">El Tesoro del Saber (ETS)</h2>'
        '</div>'
        '<div style="padding: 30px; background-color: #ffffff; color: #333;">'
        f'<p style="font-size: 18px;"><strong>¡Qué onda, {user.full_name}!'
        '</strong></p>'
        '<p>Parece que se te olvidó la contraseña. 😅</p>'
        '<p>No te preocupes, <strong>esto les pasa hasta a los mejores '
        'ingenieros</strong> (incluso a los que reprueban Cálculo, Física, '
        'Proba, Programación, toda su maldita vida).</p>'
        '<p>Haz clic en el botón de abajo para recuperar tu acceso:</p>'
        '<div style="text-align: center; margin: 30px 0;">'
        f'<a href="{link}" style="background-color: #28a745; '
        'color: white; padding: 14px 28px; text-decoration: none; '
        'border-radius: 5px; font-weight: bold; font-size: 16px; '
        'display: inline-block;">'
        'Cambiar Contraseña'
        '</a>'
        '</div>'
        '<p style="font-style: italic; color: #555;">'
        'Consejo del día: Procura que esta vez sea algo más fácil de recordar '
        '... <strong>¡como esa materia que todavía debes!</strong> 📚'
        '</p>'
        '<hr style="border: none; border-top: 1px solid #eee; '
        'margin: 20px 0;">'
        '<small style="color: #888;">'
        'Este enlace expirará en 25 minutos :D.<br>'
        'Si no fuiste tú, ignora esto (y corre a cambiar tus claves por si '
        'acaso).'
        '</small>'
        '</div>'
        '</div>'
    )

    message = MessageSchema(
        subject="Restablece tu contraseña - El Tesoro del Saber (ETS)",
        recipients=[datos.email],
        body=html,
        subtype=MessageType.html
    )

    fm = FastMail(conf)
    await fm.send_message(message)

    return {"message": "Correo enviado exitosamente"}


@router.post("/reset-password")
def reset_password(
    datos: esquemas.UserResetPassword,
    db: Session = Depends(get_db)
):
    """
    Paso 2: Aplicar el restablecimiento con el token.
    """
    try:
        payload = jwt.decode(
            datos.token,
            auth.SECRET_KEY,
            algorithms=[auth.ALGORITHM]
        )
        email: str = payload.get("sub")
        token_type: str = payload.get("type")

        if email is None or token_type != "reset":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token inválido"
            )

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El enlace ha expirado o es inválido"
        )

    user = crud.get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )

    new_hash = auth.get_password_hash(datos.new_password)
    crud.update_password(db, user.id, new_hash)

    return {"message": "Contraseña restablecida con éxito"}
