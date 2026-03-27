"""Endpoints to manage External disciplines (Externos)."""
import os
import json
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

@router.get("/externos/instituicoes")
async def list_instituicoes_externas():
    """List all available external institutions folders."""
    if not EXTERNOS_DIR.exists():
        return {"instituicoes": []}
    
    insts = [d.name for d in EXTERNOS_DIR.iterdir() if d.is_dir()]
    return {"instituicoes": sorted(insts)}

@router.get("/externos/{inst_nome}/cursos")
async def list_cursos_externos(inst_nome: str):
    """List all available external courses folders for an institution."""
    inst_dir = EXTERNOS_DIR / sanitize_filename(inst_nome)
    if not inst_dir.exists():
        return {"cursos": []}
    
    cursos = [d.name for d in inst_dir.iterdir() if d.is_dir()]
    return {"cursos": sorted(cursos)}

@router.get("/externos/{inst_nome}/{curso_nome}/disciplinas")
async def list_disciplinas_externas(inst_nome: str, curso_nome: str):
    """List all external disciplines for a given institution and course."""
    curso_dir = _get_ext_curso_dir(inst_nome, curso_nome)
    if not curso_dir.exists():
        return {"curso": curso_nome, "total": 0, "disciplinas": []}
    
    disciplinas = []
    for f in curso_dir.glob("*.json"):
        try:
            with open(f, "r", encoding="utf-8") as file:
                data = json.load(file)
                disciplinas.append(data)
        except Exception:
            pass
            
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
