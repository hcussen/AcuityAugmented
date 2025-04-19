from pydantic_settings import BaseSettings, SettingsConfigDict
import logging


class Settings(BaseSettings):
    # Add database URL for SQLAlchemy
    database_url: str = 'sqlite+pysqlite:///db.db'

    # You can add other settings as needed
    env_name: str = "dev"
    
    # Acuity API credentials
    acuity_user_id: str
    acuity_api_key: str

    # Center Hours (start, end)
    hours_open: dict = {
        0: ('16:00', '20:00'),
        1: ('16:00', '20:00'),
        2: ('16:00', '20:00'),
        3: ('16:00', '20:00'),
        4: ('16:00', '19:00'),
        5: ('10:00', '13:00'),
        6: ('00:00', '00:00')
    }
    

    model_config = SettingsConfigDict(env_file=".env")


# Create settings instance
settings = Settings()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)
