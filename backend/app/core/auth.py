from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.config import settings
from app.models.user import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка пароля"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Хеширование пароля"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Создание JWT токена"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """Аутентификация пользователя с защитой от брутфорса"""
    user = db.query(User).filter(User.username == username).first()
    
    if not user:
        return None
    
    # Проверка блокировки
    if user.locked_until and user.locked_until > datetime.utcnow():
        raise ValueError(f"Аккаунт заблокирован до {user.locked_until}")
    
    # Проверка пароля
    if not verify_password(password, user.password_hash):
        # Увеличиваем счетчик неудачных попыток
        user.failed_login_attempts += 1
        
        # Блокируем после максимального количества попыток
        if user.failed_login_attempts >= settings.brute_force_max_attempts:
            user.locked_until = datetime.utcnow() + timedelta(
                minutes=settings.brute_force_lockout_time_minutes
            )
            db.commit()
            raise ValueError(
                f"Слишком много неудачных попыток. Аккаунт заблокирован на "
                f"{settings.brute_force_lockout_time_minutes} минут"
            )
        
        db.commit()
        return None
    
    # Сбрасываем счетчик при успешной аутентификации
    user.failed_login_attempts = 0
    user.locked_until = None
    db.commit()
    
    return user


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Получение пользователя по username"""
    return db.query(User).filter(User.username == username).first()

