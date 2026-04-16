"""Endpoints to manage UFSM Courses and disciplines (CursosUFSM)."""
import os
import json
import asyncio
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from pydantic import BaseModel

from src.api.auth import get_current_user
from src.config import get_data_dir
from src.domain.enums import UserRole
from src.scripts.extract_curriculum import parse_xlsx_to_json, sanitize_filename

router = APIRouter()

CURSOS_DIR = get_data_dir() / "CursosUFSM"

class DisciplinaUpdateSchema(BaseModel):
    codigo: Optional[str] = None
    nome: Optional[str] = None
    semestre: Optional[int] = None
    tipo: Optional[str] = None
    ch_total: Optional[int] = None
    nucleo_grupo: Optional[str] = None
    programa: Optional[str] = None
    pre_requisito: Optional[List[str]] = None
    t_p_pext: Optional[str] = None

class DisciplinaCriacaoSchema(BaseModel):
    codigo: str
    nome: str
    semestre: Optional[int] = None
    tipo: str = "OBR"  # OBR, ELE, DCG, DCEX
    ch_total: int
    nucleo_grupo: Optional[str] = None
    programa: Optional[str] = None
    pre_requisito: List[str] = []
    t_p_pext: Optional[str] = None

def _get_curso_dir(curso_nome: str) -> Path:
    return CURSOS_DIR / sanitize_filename(curso_nome)

def _load_cursos_sync() -> list:
    """Blocking I/O — run in executor."""
    if not CURSOS_DIR.exists():
        return []
    return sorted(d.name for d in CURSOS_DIR.iterdir() if d.is_dir())

def _load_disciplinas_sync(curso_dir: Path) -> list:
    """Blocking I/O — run in executor."""
    disciplinas = []
    for f in curso_dir.glob("*.json"):
        try:
            with open(f, "r", encoding="utf-8") as fh:
                disciplinas.append(json.load(fh))
        except Exception:
            pass
    disciplinas.sort(key=lambda x: (x.get("semestre") or 99, x.get("nome", "")))
    return disciplinas

@router.get("/cursos")
async def list_cursos():
    """List all available UFSM courses."""
    loop = asyncio.get_event_loop()
    cursos = await loop.run_in_executor(None, _load_cursos_sync)
    return {"cursos": cursos}


@router.get("/cursos/{curso_nome}/disciplinas")
async def list_disciplinas(curso_nome: str):
    """List all disciplines for a given course."""
    curso_dir = _get_curso_dir(curso_nome)
    if not curso_dir.exists():
        raise HTTPException(status_code=404, detail="Curso não encontrado")

    loop = asyncio.get_event_loop()
    disciplinas = await loop.run_in_executor(None, _load_disciplinas_sync, curso_dir)
    return {"curso": curso_nome, "total": len(disciplinas), "disciplinas": disciplinas}


@router.patch("/cursos/{curso_nome}/disciplinas/{codigo}")
async def update_disciplina(
    curso_nome: str, 
    codigo: str, 
    payload: DisciplinaUpdateSchema,
    user=Depends(get_current_user)
):
    """Update a specific discipline. Requires COORDENACAO or ADMIN role."""
    if user.role not in [UserRole.ADMIN, UserRole.COORDENACAO]:
        raise HTTPException(status_code=403, detail="Acesso negado")
        
    curso_dir = _get_curso_dir(curso_nome)
    filepath = curso_dir / f"{sanitize_filename(codigo)}.json"
    
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Disciplina não encontrada")
        
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    update_data = payload.model_dump(exclude_unset=True)
    if not update_data:
        return data
        
    data.update(update_data)
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    return data


@router.post("/cursos/{curso_nome}/disciplinas")
async def create_disciplina(
    curso_nome: str,
    payload: DisciplinaCriacaoSchema,
    user=Depends(get_current_user)
):
    """Create a new discipline permanently in the JSON database. Creates course folder if needed."""
    if user.role not in [UserRole.ADMIN, UserRole.COORDENACAO]:
        raise HTTPException(status_code=403, detail="Acesso negado")
        
    curso_dir = _get_curso_dir(curso_nome)
    curso_dir.mkdir(parents=True, exist_ok=True)
    
    filepath = curso_dir / f"{sanitize_filename(payload.codigo)}.json"
    if filepath.exists():
        raise HTTPException(status_code=400, detail="Disciplina com este código já existe neste curso")
        
    data = payload.model_dump()
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    return data


@router.post("/cursos/upload")
async def upload_curso(
    curso_nome: str = Form(...),
    file: UploadFile = File(...),
    user=Depends(get_current_user)
):
    """Upload a new .xlsx curriculum and extract it into a dynamic CursosUFSM folder."""
    if user.role not in [UserRole.ADMIN, UserRole.COORDENACAO]:
        raise HTTPException(status_code=403, detail="Acesso negado")
        
    if not file.filename.endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="Apenas arquivos .xlsx são suportados por enquanto.")
        
    CURSOS_DIR.mkdir(parents=True, exist_ok=True)
    
    temp_path = CURSOS_DIR / f"temp_upload_{sanitize_filename(curso_nome)}.xlsx"
    
    content = await file.read()
    with open(temp_path, "wb") as f:
        f.write(content)
        
    try:
        # Call the extraction script logic directly
        parse_xlsx_to_json(temp_path, curso_nome)
    except Exception as e:
        if temp_path.exists():
            temp_path.unlink()
        raise HTTPException(status_code=500, detail=f"Erro ao processar planilha: {str(e)}")
        
    if temp_path.exists():
        temp_path.unlink()
        
    return {"status": "ok", "mensagem": f"Curso '{curso_nome}' processado com sucesso!"}
