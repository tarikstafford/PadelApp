from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    PROJECT_NAME: str = "PadelGo API"
    API_V1_STR: str = "/api/v1"

    # Database settings - No default value, will fail loudly if not in environment
    DATABASE_URL: str = Field(..., env="DATABASE_URL")

    # JWT settings
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 1 # 1 day for access token
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30 # 30 days for refresh token

    model_config = SettingsConfigDict(env_file=".env", extra='ignore')

settings = Settings() 