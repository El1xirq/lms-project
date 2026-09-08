from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
import logging
import sys


class Settings(BaseSettings):
    db_url: str = Field(validation_alias='DATABASE_URL')
    db_sync_url: str = Field(validation_alias='SYNC_DATABASE_URL')
    test_db: str = Field(validation_alias='TEST_DATABASE_URL')
    secret_key: str
    algorithm: str
    access_token_expire: int = Field(validation_alias='ACCESS_TOKEN_EXPIRE_MINUTES')
    refresh_token_expire: int = Field(validation_alias='REFRESH_TOKEN_EXPIRE_DAYS')
    debug: bool
    postgres_user: str
    postgres_password: str
    postgres_db: str

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')


settings = Settings()


def setup_logging():
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
        ]
    )
    
    return logging.getLogger(__name__)