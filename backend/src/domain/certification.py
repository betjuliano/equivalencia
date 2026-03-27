"""Domain models — Certification following Spec.md section 5.4"""
from __future__ import annotations
from typing import Optional
from pydantic import BaseModel
from .enums import AnalysisStatus, DecisaoStatus


class Coordenador(BaseModel):
    nome: str
    email: str
    user_id: str


class Certificacao(BaseModel):
    id: str
    analysis_id: str
    curso: str
    curso_slug: str
    disciplina_ufsm_codigo: str
    disciplina_ufsm_nome: str
    instituicao_origem: str
    disciplina_origem_nome: str
    status: AnalysisStatus
    decisao: DecisaoStatus
    coordenador: Coordenador
    ressalvas: Optional[str] = None
    data_certificacao: str
    ativo: bool = True
    publicavel_para_consulta: bool = True
