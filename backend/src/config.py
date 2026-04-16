"""Application — Config and settings (Spec.md section 9.1)"""
from __future__ import annotations
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Curriculum Equivalence Analyzer"
    version: str = "1.0.0"
    data_dir: str = "data"
    max_pdf_size_mb: int = 20
    jwt_secret: str = "change-me-in-production-with-a-long-secret"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 480

    coord_user: str = "coord"
    coord_password: str = "coord123"

    cursos_ufsm_dir: str = "CursosUFSM"
    externos_dir: str = "Externos"

    # Comparator weights (Spec section 7.4)
    weight_cosine_tfidf: float = 0.55
    weight_overlap_keywords: float = 0.20
    weight_ngram_similarity: float = 0.15
    weight_synonym_bonus: float = 0.10

    # Thresholds (Spec section 7.5)
    threshold_equivalente: float = 0.75
    threshold_parcial: float = 0.45

    class Config:
        env_file = Path(__file__).parent.parent.parent / ".env"
        extra = "ignore"


settings = Settings()


def get_data_dir() -> Path:
    p = Path(settings.data_dir)
    p.mkdir(parents=True, exist_ok=True)
    (p / settings.cursos_ufsm_dir).mkdir(parents=True, exist_ok=True)
    (p / settings.externos_dir).mkdir(parents=True, exist_ok=True)
    return p
