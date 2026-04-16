"""Main FastAPI app — routes, startup, dependency injection (Spec.md sections 9.1-9.9)"""
from __future__ import annotations
from pathlib import Path
import sys
import os

# Ensure src is importable when running from backend/
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings, get_data_dir
from src.infrastructure.index_store import IndexStore
from src.infrastructure.logger import setup_logger
from src.application.program_service import ProgramService
from src.application.analysis_service import AnalysisService
from src.application.certification_service import CertificationService

# ─── Global singletons ───────────────────────────────────────────────────────
DATA_DIR = Path(settings.data_dir)
UPLOAD_DIR = DATA_DIR / "uploads" / "pdf"

index_store: IndexStore = None  # type: ignore
program_service: ProgramService = None  # type: ignore
analysis_service: AnalysisService = None  # type: ignore
certification_service: CertificationService = None  # type: ignore

# ─── App ─────────────────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="Sistema de Comparação de Programas de Disciplinas — UFSM",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    global index_store, program_service, analysis_service, certification_service

    # Ensure directories
    for sub in [
        "ufsm/courses", "ufsm/disciplines",
        "externos/institutions", "externos/disciplines",
        "analises", "certificacoes", "index", "logs", "uploads/pdf",
    ]:
        (DATA_DIR / sub).mkdir(parents=True, exist_ok=True)

    setup_logger(DATA_DIR)
    index_store = IndexStore(DATA_DIR)
    program_service = ProgramService(DATA_DIR, index_store)
    analysis_service = AnalysisService(DATA_DIR, index_store, program_service)
    certification_service = CertificationService(DATA_DIR, index_store)


@app.get("/", tags=["health"])
async def root():
    return {
        "message": "Sistema de Comparação de Programas (S.ADM) API",
        "version": settings.version,
        "health_check": "/api/v1/health",
        "docs": "/docs"
    }


# ─── Routers ─────────────────────────────────────────────────────────────────
from src.api import auth_routes, programs, analyses, certifications, uploads, public_search, courses, externals

PREFIX = "/api/v1"
app.include_router(auth_routes.router, prefix=PREFIX, tags=["auth"])
app.include_router(uploads.router, prefix=PREFIX, tags=["uploads"])
app.include_router(programs.router, prefix=PREFIX, tags=["programs"])
app.include_router(analyses.router, prefix=PREFIX, tags=["analyses"])
app.include_router(certifications.router, prefix=PREFIX, tags=["certifications"])
app.include_router(public_search.router, prefix=PREFIX, tags=["public"])
app.include_router(courses.router, prefix=PREFIX, tags=["courses"])
app.include_router(externals.router, prefix=PREFIX, tags=["externos"])


@app.get("/api/v1/health", tags=["health"])
async def health():
    return {"status": "ok", "service": "curriculum-equivalence-api", "version": settings.version}
