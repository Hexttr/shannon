from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency для получения сессии БД"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Инициализация БД - создание таблиц и начального пользователя"""
    from app.models import user, service, pentest, vulnerability, log
    
    Base.metadata.create_all(bind=engine)
    
    # Создаем начального пользователя admin/513277
    db = SessionLocal()
    try:
        from app.models.user import User
        from app.core.auth import get_password_hash
        
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            admin_user = User(
                username="admin",
                email="admin@shannon.local",
                password_hash=get_password_hash("513277")
            )
            db.add(admin_user)
            db.commit()
            print("✅ Создан пользователь admin")
    except Exception as e:
        print(f"❌ Ошибка при создании пользователя: {e}")
        db.rollback()
    finally:
        db.close()


