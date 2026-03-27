"""API — Programs endpoints (Spec.md sections 10.4-10.7)"""
from __future__ import annotations
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel
from src.api.auth import get_current_user, get_current_user_optional, require_role, TokenData
from src.domain.enums import UserRole

router = APIRouter()


# ─── Request DTOs ────────────────────────────────────────────────────────────

class TextProgramRequest(BaseModel):
    tipo: str  # "ufsm" | "externo"
    codigo: str
    nome: str
    instituicao: Optional[str] = None
    curso: Optional[str] = None
    curso_ufsm: Optional[str] = None
    raw_text: str
    carga_horaria_informada: Optional[float] = None
    nota: Optional[float] = None
    aprovado: Optional[bool] = None
    modalidade: str = "presencial"
    possui_extensao: bool = False
    e_estagio: bool = False
    e_tcc: bool = False
    versao_ppc: Optional[str] = None


class PDFProgramRequest(BaseModel):
    tipo: str
    codigo: str
    nome: str
    instituicao: Optional[str] = None
    curso: Optional[str] = None
    upload_id: str
    carga_horaria_informada: Optional[float] = None
    nota: Optional[float] = None
    aprovado: Optional[bool] = None


# ─── Routes ──────────────────────────────────────────────────────────────────

def get_program_service():
    from src.main import program_service
    return program_service


@router.post("/programs/text", status_code=201)
async def create_program_from_text(
    req: TextProgramRequest,
    current_user: Optional[TokenData] = Depends(get_current_user_optional),
    svc=Depends(get_program_service),
):
    user_id = current_user.user_id if current_user else "aluno_publico"
    if req.tipo == "ufsm":
        prog = await svc.cadastrar_ufsm(
            codigo=req.codigo,
            nome=req.nome,
            curso=req.curso_ufsm or req.curso or "",
            raw_text=req.raw_text,
            carga_horaria_informada=req.carga_horaria_informada,
            modalidade=req.modalidade,
            possui_extensao=req.possui_extensao,
            e_estagio=req.e_estagio,
            e_tcc=req.e_tcc,
            versao_ppc=req.versao_ppc,
            usuario=user_id,
        )
    else:
        prog = await svc.cadastrar_externo(
            codigo=req.codigo,
            nome=req.nome,
            instituicao=req.instituicao or "Desconhecida",
            curso_origem=req.curso or "",
            raw_text=req.raw_text,
            carga_horaria_informada=req.carga_horaria_informada,
            nota=req.nota,
            aprovado=req.aprovado,
            modalidade=req.modalidade,
            possui_extensao=req.possui_extensao,
            e_estagio=req.e_estagio,
            e_tcc=req.e_tcc,
            usuario=user_id,
        )
    return {"program_id": prog.id, "status": "created"}


@router.post("/programs/pdf", status_code=201)
async def create_program_from_pdf(
    req: PDFProgramRequest,
    current_user: Optional[TokenData] = Depends(get_current_user_optional),
    svc=Depends(get_program_service),
):
    user_id = current_user.user_id if current_user else "aluno_publico"
    from src.main import UPLOAD_DIR
    import os
    pdf_path = UPLOAD_DIR / f"{req.upload_id}.pdf"
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="Upload não encontrado")

    prog = await svc.cadastrar_externo_por_pdf(
        pdf_path=pdf_path,
        codigo=req.codigo,
        nome=req.nome,
        instituicao=req.instituicao or "Desconhecida",
        curso_origem=req.curso or "",
        carga_horaria_informada=req.carga_horaria_informada,
        nota=req.nota,
        aprovado=req.aprovado,
        usuario=user_id,
    )
    return {"program_id": prog.id, "status": "created"}


@router.get("/programs/{program_id}")
async def get_program(
    program_id: str,
    svc=Depends(get_program_service),
):
    prog = await svc.get_program(program_id)
    if not prog:
        raise HTTPException(status_code=404, detail="Programa não encontrado")
    return prog


@router.get("/ufsm/disciplines")
async def search_ufsm_disciplines(
    curso: Optional[str] = None,
    query: Optional[str] = None,
    svc=Depends(get_program_service),
):
    return await svc.search_ufsm(curso, query)
