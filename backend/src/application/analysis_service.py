"""Application — AnalysisService: create, compare, and retrieve analyses"""
from __future__ import annotations
from pathlib import Path
from typing import Optional, List, Dict
from datetime import datetime, timezone

from src.domain.analysis import Analise, WorkloadInfo, MetadadosAnalise, Alerta
from src.domain.enums import AnalysisStatus, CargoHorariaFonte
from src.infrastructure.file_store import write_json_atomic, read_json
from src.infrastructure.file_store import short_hash
from src.infrastructure.index_store import IndexStore
from src.infrastructure.comparator import compare_programs, calculate_content_score, calculate_workload_score
from src.infrastructure.parser import collect_items
from src.infrastructure.logger import log_audit
from src.infrastructure.curriculum_loader import discipline_in_standard, CurriculumLoadError
from src.utils import now_iso, timestamp_compact


class AnalysisService:
    def __init__(self, data_dir: Path, index_store: IndexStore, program_service):
        self.data_dir = data_dir
        self.index_store = index_store
        self.program_service = program_service

    def _path(self, analysis_id: str) -> Path:
        return self.data_dir / "analises" / f"{analysis_id}.json"

    async def create_analysis(
        self,
        ufsm_program_id: str,
        external_program_id: Optional[str] = None,
        threshold_content: float = 75.0,
        threshold_workload: float = 75.0,
        reprocess: bool = False,
        usuario: Optional[str] = None,
        external_program_ids: Optional[List[str]] = None,
    ) -> Analise:
        ts = timestamp_compact()
        ext_ids = external_program_ids or []
        if external_program_id and external_program_id not in ext_ids:
            ext_ids.append(external_program_id)
        if not ext_ids:
            raise ValueError("Nenhum programa externo informado")
            
        primary_ext_id = ext_ids[0]
        h = short_hash(f"{ufsm_program_id}_{primary_ext_id}_{ts}")
        analysis_id = f"analise_{ts}_{h}"

        # Check for reuse
        reused_from = None
        if not reprocess:
            reusable = await self.index_store.search_reusable_analyses(ufsm_program_id)
            for r in reusable:
                if r.get("external_program_id") == primary_ext_id and r.get("resultado_final") not in [
                    AnalysisStatus.RASCUNHO, AnalysisStatus.PROCESSANDO
                ]:
                    reused_from = r.get("id")
                    break

        # Load programs
        ufsm_data = await self.program_service.get_program(ufsm_program_id)
        if not ufsm_data:
            raise ValueError("Programa UFSM não encontrado")

        ext_programs = []
        for eid in ext_ids:
            d = await self.program_service.get_program(eid)
            if d: ext_programs.append(d)
            
        if not ext_programs:
            raise ValueError("Programa(s) externo(s) não encontrado(s)")

        # Collect text items for comparison
        from src.domain.program import ProgramaEstruturado
        ufsm_struct = ProgramaEstruturado(**ufsm_data.get("programa_estruturado", {"unidades": []}))
        ufsm_items = collect_items(ufsm_struct)

        ext_items = []
        ext_ch_total = 0.0
        ext_ch_missing = False
        tem_estagio = False
        tem_tcc = False
        has_reprovado = False

        for ext_data in ext_programs:
            struct = ProgramaEstruturado(**ext_data.get("programa_estruturado", {"unidades": []}))
            ext_items.extend(collect_items(struct))
            
            ch = ext_data.get("carga_horaria")
            if ch is not None:
                ext_ch_total += float(ch)
            else:
                ext_ch_missing = True

            if ext_data.get("e_estagio"): tem_estagio = True
            if ext_data.get("e_tcc"): tem_tcc = True
            if ext_data.get("aprovado") is False: has_reprovado = True

        # Run comparison
        matches = compare_programs(ufsm_items, ext_items)
        content_score = calculate_content_score(matches)

        # Workload (Administracao specific: exclude EAD from analysis)
        ufsm_curso = ufsm_data.get("curso", "")
        # Normalização do curso para garantir match
        from src.scripts.extract_curriculum import sanitize_filename
        is_adm = (sanitize_filename(ufsm_curso) == "Administracao")

        def _get_eff_ch(prog_data):
            tp = prog_data.get("t_p_pext")
            total = float(prog_data.get("carga_horaria") or 0)
            if is_adm and tp and "-" in str(tp):
                parts = str(tp).split("-")
                if len(parts) >= 4:
                    # T-P-PEXT-EAD -> Sum T, P and PEXT
                    try:
                        pts = [float(p) for p in parts[:3] if p.strip()]
                        return sum(pts)
                    except ValueError:
                        return total
            return total

        ufsm_ch_eff = _get_eff_ch(ufsm_data)
        ext_ch_eff = 0.0
        for ext_data in ext_programs:
            ext_ch_eff += _get_eff_ch(ext_data)

        # Scorig logic using effective CH
        workload_score = calculate_workload_score(ufsm_ch_eff or 0, ext_ch_eff or 0) if ufsm_ch_eff and ext_ch_eff else None
        
        # Real totals for display
        ufsm_ch = ufsm_data.get("carga_horaria")
        ext_ch = ext_ch_total if not ext_ch_missing else None

        # Determine technical result
        alertas: List[Alerta] = []

        # Curriculum standard validation (soft check — never blocks the analysis)
        ufsm_nome = ufsm_data.get("nome", "")
        if ufsm_nome and not discipline_in_standard(ufsm_nome):
            alertas.append(Alerta(
                tipo="disciplina_fora_matriz",
                mensagem=(
                    f"A disciplina UFSM '{ufsm_nome}' não foi localizada na matriz curricular "
                    "padrão (matriz_curricular_editavel.xlsx). Verifique se o nome está correto "
                    "ou se a disciplina pertence à grade atual."
                ),
                nivel="warning",
            ))

        if ufsm_ch is None:
            alertas.append(Alerta(tipo="carga_horaria_faltante", mensagem="Carga horária da disciplina UFSM não identificada. Informe manualmente.", nivel="warning"))
        if ext_ch_missing:
            alertas.append(Alerta(tipo="carga_horaria_faltante", mensagem="Carga horária de um ou mais programas externos pendente. Informe manualmente na tela de workload.", nivel="warning"))

        # Normative alerts
        if tem_estagio:
            alertas.append(Alerta(tipo="estagio", mensagem="Disciplina externa caracterizada como estágio — verificar compatibilidade normativa.", nivel="warning"))
        if tem_tcc:
            alertas.append(Alerta(tipo="tcc", mensagem="Disciplina externa caracterizada como TCC — verificar compatibilidade normativa.", nivel="warning"))
        if has_reprovado:
            alertas.append(Alerta(tipo="reprovado", mensagem="Estudante não aprovado na disciplina de origem.", nivel="error"))

        # Technical result
        if workload_score is None:
            resultado_tecnico = AnalysisStatus.PENDENTE_DADOS
        elif content_score >= threshold_content and workload_score >= threshold_workload:
            resultado_tecnico = AnalysisStatus.PRE_APROVAVEL_TECNICAMENTE
        else:
            resultado_tecnico = AnalysisStatus.NAO_ATENDE_TECNICAMENTE

        resultado_final = (
            AnalysisStatus.PENDENTE_DADOS if workload_score is None
            else AnalysisStatus.PENDENTE_CERTIFICACAO if resultado_tecnico == AnalysisStatus.PRE_APROVAVEL_TECNICAMENTE
            else AnalysisStatus.NAO_ATENDE_TECNICAMENTE
        )

        obs_lines = [
            f"Score de conteúdo: {content_score:.2f}% (limiar: {threshold_content}%)",
            f"Score de carga horária: {workload_score:.2f}% (limiar: {threshold_workload}%)" if workload_score else "Carga horária pendente de informação manual.",
            f"Total de itens comparados (UFSM): {len(matches)}",
        ]

        analise = Analise(
            id=analysis_id,
            ufsm_program_id=ufsm_program_id,
            external_program_id=primary_ext_id,
            external_program_ids=ext_ids,
            threshold_content=threshold_content,
            threshold_workload=threshold_workload,
            content_score=content_score,
            workload_score=workload_score,
            resultado_tecnico=resultado_tecnico,
            resultado_final=resultado_final,
            reused_from_analysis_id=reused_from,
            workload=WorkloadInfo(
                ufsm=ufsm_ch,
                externo=ext_ch,
                fonte_ufsm=ufsm_data.get("carga_horaria_fonte"),
                fonte_externo="Múltiplos" if len(ext_ids) > 1 else ext_programs[0].get("carga_horaria_fonte"),
            ),
            matches=matches,
            alertas=alertas,
            observacoes_tecnicas="\n".join(obs_lines),
            metadados=MetadadosAnalise(criado_por=usuario, criado_em=now_iso()),
        )

        await write_json_atomic(self._path(analysis_id), analise.model_dump())
        await self.index_store.add_analise({
            "id": analysis_id,
            "ufsm_program_id": ufsm_program_id,
            "external_program_id": primary_ext_id,
            "external_program_ids": ext_ids,
            "content_score": content_score,
            "workload_score": workload_score,
            "resultado_tecnico": resultado_tecnico,
            "resultado_final": resultado_final,
            "criado_em": now_iso(),
        })
        log_audit("criar_analise", usuario, [analysis_id])
        return analise

    async def get_analysis(self, analysis_id: str) -> Optional[Dict]:
        return await read_json(self._path(analysis_id))

    async def search_reusable(self, ufsm_program_id: str, external_query: Optional[str] = None) -> List[Dict]:
        return await self.index_store.search_reusable_analyses(ufsm_program_id, external_query)

    async def update_workload(self, analysis_id: str, ufsm_ch: Optional[float], ext_ch: Optional[float]) -> Dict:
        """Manually provide missing workload and recompute workload score."""
        data = await read_json(self._path(analysis_id))
        if not data:
            raise ValueError("Análise não encontrada")

        data["workload"]["ufsm"] = ufsm_ch or data["workload"].get("ufsm")
        data["workload"]["externo"] = ext_ch or data["workload"].get("externo")

        u = data["workload"]["ufsm"]
        e = data["workload"]["externo"]
        if u and e:
            ws = calculate_workload_score(u, e)
            data["workload_score"] = ws
            if data["content_score"] >= data["threshold_content"] and ws >= data["threshold_workload"]:
                data["resultado_tecnico"] = AnalysisStatus.PRE_APROVAVEL_TECNICAMENTE
                data["resultado_final"] = AnalysisStatus.PENDENTE_CERTIFICACAO
            else:
                data["resultado_tecnico"] = AnalysisStatus.NAO_ATENDE_TECNICAMENTE
                data["resultado_final"] = AnalysisStatus.NAO_ATENDE_TECNICAMENTE

        await write_json_atomic(self._path(analysis_id), data)
        return data
