"""Domain models — Analysis following Spec.md section 5.3"""
from __future__ import annotations
from typing import Optional, List
from pydantic import BaseModel, Field
from .enums import AnalysisStatus, MatchClassification


class WorkloadInfo(BaseModel):
    ufsm: Optional[float] = None
    externo: Optional[float] = None
    fonte_ufsm: Optional[str] = None
    fonte_externo: Optional[str] = None


class MatchItem(BaseModel):
    ufsm_item: str
    externo_item: Optional[str] = None
    score_bruto: float = 0.0
    score_final: float = 0.0
    palavras_coincidentes: List[str] = []
    bonus_sinonimos: bool = False
    classificacao: MatchClassification = MatchClassification.AUSENTE
    pontuacao: float = 0.0  # 1.0 / 0.5 / 0.0


class Alerta(BaseModel):
    tipo: str
    mensagem: str
    nivel: str = "info"  # info | warning | error


class MetadadosAnalise(BaseModel):
    criado_por: Optional[str] = None
    criado_em: str
    algoritmo_versao: str = "1.0.0"


class Analise(BaseModel):
    id: str
    ufsm_program_id: str
    external_program_id: Optional[str] = None
    external_program_ids: list[str] = []
    threshold_content: float = 75.0
    threshold_workload: float = 75.0
    content_score: Optional[float] = None
    workload_score: Optional[float] = None
    resultado_tecnico: Optional[AnalysisStatus] = None
    resultado_final: AnalysisStatus = AnalysisStatus.RASCUNHO
    reused_from_analysis_id: Optional[str] = None
    workload: WorkloadInfo = Field(default_factory=WorkloadInfo)
    matches: List[MatchItem] = []
    alertas: List[Alerta] = []
    observacoes_tecnicas: Optional[str] = None
    metadados: MetadadosAnalise
