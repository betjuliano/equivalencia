"""Endpoints to manage External disciplines (Externos)."""
import os
import json
import asyncio
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Form
from pydantic import BaseModel

from src.api.auth import get_current_user
from src.config import settings, get_data_dir
from src.domain.enums import UserRole
from src.scripts.extract_curriculum import sanitize_filename

router = APIRouter()

EXTERNOS_DIR = get_data_dir() / settings.externos_dir

class DisciplinaExternaSchema(BaseModel):
    codigo: str
    nome: str
    instituicao: str
    curso_origem: str
    ch_total: int
    programa: str  # Texto da ementa
    semestre: Optional[int] = None
    tipo: Optional[str] = "EXT"

def _get_ext_curso_dir(inst_nome: str, curso_nome: str) -> Path:
    return EXTERNOS_DIR / sanitize_filename(inst_nome) / sanitize_filename(curso_nome)

def _load_instituicoes_sync() -> list:
    """Blocking I/O — run in executor."""
    if not EXTERNOS_DIR.exists():
        return []
    return sorted(d.name for d in EXTERNOS_DIR.iterdir() if d.is_dir())

def _load_cursos_externos_sync(inst_dir: Path) -> list:
    """Blocking I/O — run in executor."""
    if not inst_dir.exists():
        return []
    return sorted(d.name for d in inst_dir.iterdir() if d.is_dir())

def _load_disciplinas_externas_sync(curso_dir: Path) -> list:
    """Blocking I/O — run in executor."""
    disciplinas = []
    for f in curso_dir.glob("*.json"):
        try:
            with open(f, "r", encoding="utf-8") as fh:
                disciplinas.append(json.load(fh))
        except Exception:
            pass
    return disciplinas

@router.get("/externos/instituicoes")
async def list_instituicoes_externas():
    """List all available external institutions folders."""
    loop = asyncio.get_event_loop()
    insts = await loop.run_in_executor(None, _load_instituicoes_sync)
    return {"instituicoes": insts}

@router.get("/externos/{inst_nome}/cursos")
async def list_cursos_externos(inst_nome: str):
    """List all available external courses folders for an institution."""
    inst_dir = EXTERNOS_DIR / sanitize_filename(inst_nome)
    loop = asyncio.get_event_loop()
    cursos = await loop.run_in_executor(None, _load_cursos_externos_sync, inst_dir)
    return {"cursos": cursos}

@router.get("/externos/{inst_nome}/{curso_nome}/disciplinas")
async def list_disciplinas_externas(inst_nome: str, curso_nome: str):
    """List all external disciplines for a given institution and course."""
    curso_dir = _get_ext_curso_dir(inst_nome, curso_nome)
    if not curso_dir.exists():
        return {"curso": curso_nome, "total": 0, "disciplinas": []}
    loop = asyncio.get_event_loop()
    disciplinas = await loop.run_in_executor(None, _load_disciplinas_externas_sync, curso_dir)
    return {"curso": curso_nome, "total": len(disciplinas), "inst": inst_nome, "disciplinas": disciplinas}

@router.post("/externos/{inst_nome}/{curso_nome}/disciplinas")
async def create_disciplina_externa(
    inst_nome: str,
    curso_nome: str,
    payload: DisciplinaExternaSchema
):
    """Create a new external discipline permanently. Public access authorized by PM."""
    curso_dir = _get_ext_curso_dir(inst_nome, curso_nome)
    curso_dir.mkdir(parents=True, exist_ok=True)
    
    filepath = curso_dir / f"{sanitize_filename(payload.codigo)}.json"
    
    # Save as JSON
    data = payload.model_dump()
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    return data
