from pydantic_settings import BaseSettings, SettingsConfigDict
import logging


class Settings(BaseSettings):
    # # Add database URL for SQLAlchemy
    database_url: str = 'sqlite+pysqlite:///db.db'

    # You can add other settings as needed
    env_name: str = "dev"

    model_config = SettingsConfigDict(env_file=".env")


# Create settings instance
settings = Settings()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)
