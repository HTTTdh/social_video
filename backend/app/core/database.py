# app/core/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.settings import get_settings

settings = get_settings()
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    from app.models.base import Base
    import app.models.auth_models
    import app.models.roles_models
    import app.models.channel_models
    import app.models.media_models
    import app.models.post_models
    import app.models.video_models
    import app.models.template_models
    import app.models.schedule_models
    import app.models.analytics_models
    import app.models.association  

    Base.metadata.create_all(bind=engine)
