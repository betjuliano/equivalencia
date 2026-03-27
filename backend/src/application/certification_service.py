"""Application — CertificationService: formal certification flow (Spec.md section F07)"""
from __future__ import annotations
from pathlib import Path
from typing import Optional, Dict
from datetime import datetime, timezone

from src.domain.certification import Certificacao, Coordenador
from src.domain.enums import AnalysisStatus, DecisaoStatus
from src.infrastructure.file_store import write_json_atomic, read_json, short_hash
from src.infrastructure.index_store import IndexStore
from src.infrastructure.logger import log_audit
from src.utils import now_iso, today_str, slugify


class CertificationService:
    def __init__(self, data_dir: Path, index_store: IndexStore):
        self.data_dir = data_dir
        self.index_store = index_store

    def _path(self, cert_id: str) -> Path:
        return self.data_dir / "certificacoes" / f"{cert_id}.json"

    async def certify(
        self,
        analysis_data: Dict,
        decisao: DecisaoStatus,
        status: AnalysisStatus,
        coordenador_nome: str,
        coordenador_email: str,
        coordenador_user_id: str,
        ressalvas: Optional[str] = None,
        publicavel_para_consulta: bool = True,
    ) -> Certificacao:
        # Hydrate related info from analysis
        ufsm_id: str = analysis_data["ufsm_program_id"]
        ext_id: str = analysis_data["external_program_id"]
        analysis_id: str = analysis_data["id"]

        # Build cert ID from curso + disciplina + hash
        codigo = ufsm_id.replace("ufsm_", "")
        h = short_hash(f"{analysis_id}_{today_str()}")
        cert_id = f"certificacao_{codigo}_{h}"

        cert = Certificacao(
            id=cert_id,
            analysis_id=analysis_id,
            curso=analysis_data.get("curso", ""),
            curso_slug=slugify(analysis_data.get("curso", "")),
            disciplina_ufsm_codigo=codigo,
            disciplina_ufsm_nome=analysis_data.get("disciplina_ufsm_nome", ""),
            instituicao_origem=analysis_data.get("instituicao_origem", ""),
            disciplina_origem_nome=analysis_data.get("disciplina_origem_nome", ""),
            status=status,
            decisao=decisao,
            coordenador=Coordenador(
                nome=coordenador_nome,
                email=coordenador_email,
                user_id=coordenador_user_id,
            ),
            ressalvas=ressalvas,
            data_certificacao=now_iso(),
            ativo=True,
            publicavel_para_consulta=publicavel_para_consulta,
        )

        await write_json_atomic(self._path(cert_id), cert.model_dump())
        await self.index_store.add_certificacao({
            "id": cert_id,
            "analysis_id": analysis_id,
            "disciplina_ufsm_codigo": codigo,
            "status": status,
            "decisao": decisao,
            "data_certificacao": today_str(),
        })

        if publicavel_para_consulta and status == AnalysisStatus.CERTIFICADA:
            await self.index_store.upsert_consulta_publica({
                "curso_slug": cert.curso_slug,
                "curso": cert.curso,
                "disciplina_codigo": codigo,
                "disciplina_nome": cert.disciplina_ufsm_nome,
                "instituicao_origem": cert.instituicao_origem,
                "disciplina_origem_nome": cert.disciplina_origem_nome,
                "certificacao_id": cert_id,
                "status": "certificada",
                "data_certificacao": today_str(),
            })

        log_audit("certificar_analise", coordenador_user_id, [cert_id, analysis_id])
        return cert

    async def get_certification(self, cert_id: str) -> Optional[Dict]:
        return await read_json(self._path(cert_id))
