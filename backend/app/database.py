from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,     # Check connection before using from pool
    pool_recycle=1800,      # Recycle connections after 30 minutes
    pool_size=5,            # Maintain a small pool of connections
    max_overflow=10,        # Allow up to 10 overflow connections
    echo=False, 
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency for FastAPI routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
