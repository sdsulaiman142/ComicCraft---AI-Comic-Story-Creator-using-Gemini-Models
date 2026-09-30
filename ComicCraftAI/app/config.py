from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    app_name: str = "ComicCraft"

    # Set MOCK_MODE=true for testing without AI APIs.
    # Set MOCK_MODE=false for real Gemini + Hugging Face generation.
    mock_mode: bool = True

    # -------------------------
    # Gemini
    # -------------------------
    gemini_api_key: str | None = None

    gemini_outline_model: str = "gemini-3.5-flash"
    gemini_story_model: str = "gemini-3.5-flash"

    # -------------------------
    # Hugging Face
    # -------------------------
    hf_token: str | None = None
    hf_api_key: str | None = None

    hf_image_model: str = "black-forest-labs/FLUX.1-schnell"
    hf_provider: str = "auto"

    # -------------------------
    # Comic
    # -------------------------
    panel_count: int = 5

    # -------------------------
    # Image generation
    # -------------------------
    image_width: int = 768
    image_height: int = 768
    image_steps: int = 4
    image_guidance: float = 3.5

    # -------------------------
    # Server
    # -------------------------
    host: str = "127.0.0.1"
    port: int = 8000

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()


# -------------------------
# Directories
# -------------------------

STATIC_DIR = BASE_DIR / "static"

PANELS_DIR = STATIC_DIR / "panels"

EXPORTS_DIR = STATIC_DIR / "exports"

TEMPLATES_DIR = BASE_DIR / "templates"


PANELS_DIR.mkdir(
    parents=True,
    exist_ok=True
)

EXPORTS_DIR.mkdir(
    parents=True,
    exist_ok=True
)