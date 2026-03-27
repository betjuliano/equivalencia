"""API — Analyses endpoints (Spec.md sections 10.8-10.10)"""
from __future__ import annotations
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from src.api.auth import get_current_user, get_current_user_optional, require_role, TokenData
from src.domain.enums import UserRole

router = APIRouter()

@router.get("/analyses", response_model=list[dict])
async def list_all_analyses(
    current_user: TokenData = Depends(require_role(UserRole.ADMIN, UserRole.COORDENACAO))
):
    """List all analyses for dashboard."""
    from src.main import index_store
    return await index_store.search_reusable_analyses("")


class CreateAnalysisRequest(BaseModel):
    ufsm_program_id: str
    external_program_id: Optional[str] = None
    external_program_ids: list[str] = []
    threshold_content: float = 75.0
    threshold_workload: float = 75.0
    reprocess: bool = False


class UpdateWorkloadRequest(BaseModel):
    ufsm_carga_horaria: Optional[float] = None
    externo_carga_horaria: Optional[float] = None


def get_analysis_service():
    from src.main import analysis_service
    return analysis_service


@router.post("/analyses", status_code=201)
async def create_analysis(
    req: CreateAnalysisRequest,
    current_user: Optional[TokenData] = Depends(get_current_user_optional),
    svc=Depends(get_analysis_service),
):
    try:
        analise = await svc.create_analysis(
            ufsm_program_id=req.ufsm_program_id,
            external_program_id=req.external_program_id,
            external_program_ids=req.external_program_ids,
            threshold_content=req.threshold_content,
            threshold_workload=req.threshold_workload,
            reprocess=req.reprocess,
            usuario=current_user.user_id if current_user else "aluno_publico",
        )
        return {
            "analysis_id": analise.id,
            "status": analise.resultado_final,
            "content_score": analise.content_score,
            "workload_score": analise.workload_score,
            "resultado_tecnico": analise.resultado_tecnico,
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/analyses/reuse")
async def get_reusable_analyses(
    ufsm_program_id: str,
    external_query: Optional[str] = None,
    current_user: TokenData = Depends(get_current_user),
    svc=Depends(get_analysis_service),
):
    return await svc.search_reusable(ufsm_program_id, external_query)


@router.get("/analyses/{analysis_id}")
async def get_analysis(
    analysis_id: str,
    svc=Depends(get_analysis_service),
):
    data = await svc.get_analysis(analysis_id)
    if not data:
        raise HTTPException(status_code=404, detail="Análise não encontrada")
    return data


@router.patch("/analyses/{analysis_id}/workload")
async def update_workload(
    analysis_id: str,
    req: UpdateWorkloadRequest,
    current_user: TokenData = Depends(require_role(UserRole.ADMIN, UserRole.SECRETARIA, UserRole.COORDENACAO)),
    svc=Depends(get_analysis_service),
):
    try:
        data = await svc.update_workload(analysis_id, req.ufsm_carga_horaria, req.externo_carga_horaria)
        return {"analysis_id": analysis_id, "workload_score": data.get("workload_score"), "resultado_final": data.get("resultado_final")}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
