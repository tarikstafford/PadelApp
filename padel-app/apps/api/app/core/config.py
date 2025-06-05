from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "PadelGo API"
    API_V1_STR: str = "/api/v1"

    # Database settings
    DATABASE_URL: str = "postgresql://user:password@host:port/db"

    # JWT settings
    SECRET_KEY: str = "your-super-secret-key-please-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 1 # 1 day for access token
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30 # 30 days for refresh token

    model_config = SettingsConfigDict(env_file=".env", extra='ignore')

settings = Settings() 