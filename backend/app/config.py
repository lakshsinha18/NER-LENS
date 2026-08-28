from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "NER-LENS API"
    environment: str = "demo"
    database_url: str = "sqlite:///./ner_lens_demo.db"
    jwt_secret: str = "change-this-demo-secret-before-production"
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 480
    cors_origins: str = "http://localhost:5173,http://localhost:8080"
    upload_dir: str = "./uploads"
    demo_mode: bool = True
    model_path: str = "../../ml/models/landslide_model.pkl"
    max_upload_mb: int = 10
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    @property
    def upload_path(self) -> Path:
        path = Path(self.upload_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path


@lru_cache
def get_settings() -> Settings:
    return Settings()
