"""API — Certifications endpoints (Spec.md sections 10.11-10.12)"""
from __future__ import annotations
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from src.api.auth import get_current_user, require_role, TokenData
from src.domain.enums import UserRole, DecisaoStatus, AnalysisStatus

router = APIRouter()


class CertifyRequest(BaseModel):
    analysis_id: str
    decisao: DecisaoStatus
    status: AnalysisStatus = AnalysisStatus.CERTIFICADA
    ressalvas: Optional[str] = None
    publicavel_para_consulta: bool = True
    # Meta for analysis display
    curso: Optional[str] = None
    disciplina_ufsm_nome: Optional[str] = None
    instituicao_origem: Optional[str] = None
    disciplina_origem_nome: Optional[str] = None


def get_cert_service():
    from src.main import certification_service
    return certification_service


def get_analysis_service():
    from src.main import analysis_service
    return analysis_service


@router.post("/certifications", status_code=201)
async def certify(
    req: CertifyRequest,
    current_user: TokenData = Depends(require_role(UserRole.ADMIN, UserRole.COORDENACAO)),
    cert_svc=Depends(get_cert_service),
    analysis_svc=Depends(get_analysis_service),
):
    analysis_data = await analysis_svc.get_analysis(req.analysis_id)
    if not analysis_data:
        raise HTTPException(status_code=404, detail="Análise não encontrada")

    # Enrich analysis_data with display metadata if provided
    analysis_data["curso"] = req.curso or analysis_data.get("curso", "")
    analysis_data["disciplina_ufsm_nome"] = req.disciplina_ufsm_nome or analysis_data.get("disciplina_ufsm_nome", "")
    analysis_data["instituicao_origem"] = req.instituicao_origem or analysis_data.get("instituicao_origem", "")
    analysis_data["disciplina_origem_nome"] = req.disciplina_origem_nome or analysis_data.get("disciplina_origem_nome", "")

    cert = await cert_svc.certify(
        analysis_data=analysis_data,
        decisao=req.decisao,
        status=req.status,
        coordenador_nome=current_user.nome,
        coordenador_email=current_user.email,
        coordenador_user_id=current_user.user_id,
        ressalvas=req.ressalvas,
        publicavel_para_consulta=req.publicavel_para_consulta,
    )
    return {"certification_id": cert.id, "status": cert.status}


@router.get("/certifications/{certification_id}")
async def get_certification(
    certification_id: str,
    current_user: TokenData = Depends(get_current_user),
    cert_svc=Depends(get_cert_service),
):
    cert = await cert_svc.get_certification(certification_id)
    if not cert:
        raise HTTPException(status_code=404, detail="Certificação não encontrada")
    return cert
