"""Application — ProgramService: cadastra e busca programas UFSM e externos"""
from __future__ import annotations
import hashlib
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone

from src.domain.program import ProgramaUFSM, ProgramaExterno, MetadadosPrograma, ProgramaEstruturado, Bibliografia
from src.domain.enums import TipoPrograma, CargoHorariaFonte
from src.infrastructure.file_store import write_json_atomic, read_json
from src.infrastructure.index_store import IndexStore
from src.infrastructure.parser import parse_program, extract_bibliography
from src.infrastructure.pdf_extractor import extract_text_from_pdf
from src.infrastructure.logger import log_audit
from src.utils import slugify, now_iso, timestamp_compact
from src.config import get_data_dir
from src.infrastructure.file_store import short_hash


class ProgramService:
    def __init__(self, data_dir: Path, index_store: IndexStore):
        self.data_dir = data_dir
        self.index_store = index_store

    def _ufsm_path(self, curso: str, codigo: str) -> Path:
        from src.scripts.extract_curriculum import sanitize_filename
        return self.data_dir / "CursosUFSM" / sanitize_filename(curso) / f"{sanitize_filename(codigo)}.json"

    def _ext_path(self, instituicao: str, curso: str, codigo: str) -> Path:
        from src.scripts.extract_curriculum import sanitize_filename
        return self.data_dir / "Externos" / sanitize_filename(instituicao) / sanitize_filename(curso) / f"{sanitize_filename(codigo)}.json"

    async def cadastrar_ufsm(
        self,
        codigo: str,
        nome: str,
        curso: str,
        raw_text: str,
        carga_horaria_informada: Optional[float] = None,
        modalidade: str = "presencial",
        possui_extensao: bool = False,
        e_estagio: bool = False,
        e_tcc: bool = False,
        versao_ppc: Optional[str] = None,
        usuario: Optional[str] = None,
    ) -> ProgramaUFSM:
        slug = slugify(nome)
        curso_slug = slugify(curso)
        programa_id = f"ufsm_{codigo}"

        estruturado, ch, fonte, _ = parse_program(raw_text)
        if carga_horaria_informada is not None:
            ch = carga_horaria_informada
            fonte = CargoHorariaFonte.MANUAL

        basica, complementar = extract_bibliography(raw_text)

        programa = ProgramaUFSM(
            id=programa_id,
            codigo=codigo,
            nome=nome,
            slug=slug,
            curso=curso,
            curso_slug=curso_slug,
            carga_horaria=ch,
            carga_horaria_fonte=fonte,
            modalidade=modalidade,
            possui_extensao=possui_extensao,
            e_estagio=e_estagio,
            e_tcc=e_tcc,
            programa_original=raw_text,
            programa_estruturado=estruturado,
            bibliografia=Bibliografia(basica=basica, complementar=complementar),
            metadados=MetadadosPrograma(
                versao_ppc=versao_ppc,
                origem_importacao="cadastro_admin",
                criado_em=now_iso(),
                atualizado_em=now_iso(),
            ),
        )

        path = self._ufsm_path(curso, codigo)
        await write_json_atomic(path, programa.model_dump())
        await self.index_store.add_ufsm_program({
            "id": programa_id,
            "codigo": codigo,
            "nome": nome,
            "slug": slug,
            "curso": curso,
            "curso_slug": curso_slug,
            "carga_horaria": ch,
        })
        log_audit("criar_programa_ufsm", usuario, [programa_id])
        return programa

    async def cadastrar_externo(
        self,
        codigo: str,
        nome: str,
        instituicao: str,
        curso_origem: str,
        raw_text: str,
        carga_horaria_informada: Optional[float] = None,
        nota: Optional[float] = None,
        aprovado: Optional[bool] = None,
        modalidade: str = "presencial",
        possui_extensao: bool = False,
        e_estagio: bool = False,
        e_tcc: bool = False,
        arquivo_origem: Optional[str] = None,
        usuario: Optional[str] = None,
    ) -> ProgramaExterno:
        inst_slug = slugify(instituicao)
        hash_id = short_hash(f"{codigo}_{inst_slug}")
        programa_id = f"ext_{inst_slug}_{slugify(nome)}_{hash_id}"

        estruturado, ch, fonte, _ = parse_program(raw_text)
        if carga_horaria_informada is not None:
            ch = carga_horaria_informada
            fonte = CargoHorariaFonte.MANUAL

        basica, complementar = extract_bibliography(raw_text)

        programa = ProgramaExterno(
            id=programa_id,
            codigo=codigo,
            nome=nome,
            instituicao=instituicao,
            instituicao_slug=inst_slug,
            curso_origem=curso_origem,
            carga_horaria=ch,
            carga_horaria_fonte=fonte,
            modalidade=modalidade,
            nota=nota,
            aprovado=aprovado,
            possui_extensao=possui_extensao,
            e_estagio=e_estagio,
            e_tcc=e_tcc,
            programa_original=raw_text,
            programa_estruturado=estruturado,
            bibliografia=Bibliografia(basica=basica, complementar=complementar),
            metadados=MetadadosPrograma(
                arquivo_origem=arquivo_origem,
                origem_importacao="envio_usuario",
                criado_em=now_iso(),
                atualizado_em=now_iso(),
            ),
        )

        path = self._ext_path(instituicao, curso_origem, codigo)
        path.parent.mkdir(parents=True, exist_ok=True)
        await write_json_atomic(path, programa.model_dump())
        await self.index_store.add_external_program({
            "id": programa_id,
            "codigo": codigo,
            "nome": nome,
            "instituicao": instituicao,
            "instituicao_slug": inst_slug,
            "carga_horaria": ch,
        })
        log_audit("criar_programa_externo", usuario, [programa_id])
        return programa

    async def get_program(self, program_id: str) -> Optional[Dict]:
        # Try UFSM index
        ufsm_items = await self.index_store.search_ufsm_programs()
        for item in ufsm_items:
            if item["id"] == program_id:
                # Find the file
                curso = item.get("curso", "Desconhecido")
                codigo = item.get("codigo", "")
                path = self._ufsm_path(curso, codigo)
                return await read_json(path)

        # Try external index
        ext_items = await self.index_store.search_external_programs()
        for item in ext_items:
            if item["id"] == program_id:
                # We need inst, curso and codigo for the new path
                instituicao = item.get("instituicao", "Desconhecida")
                curso = item.get("curso_origem", item.get("curso", "Desconhecido"))
                codigo = item.get("codigo", "S_COD")
                path = self._ext_path(instituicao, curso, codigo)
                return await read_json(path)
        return None

    async def search_ufsm(self, curso: Optional[str] = None, query: Optional[str] = None) -> List[Dict]:
        return await self.index_store.search_ufsm_programs(curso, query)

    async def cadastrar_externo_por_pdf(
        self,
        pdf_path: Path,
        codigo: str,
        nome: str,
        instituicao: str,
        curso_origem: str,
        carga_horaria_informada: Optional[float] = None,
        nota: Optional[float] = None,
        aprovado: Optional[bool] = None,
        usuario: Optional[str] = None,
    ) -> ProgramaExterno:
        text = await extract_text_from_pdf(pdf_path)
        if not text:
            text = f"[Texto não extraído de {pdf_path.name}]"
        return await self.cadastrar_externo(
            codigo=codigo,
            nome=nome,
            instituicao=instituicao,
            curso_origem=curso_origem,
            raw_text=text,
            carga_horaria_informada=carga_horaria_informada,
            nota=nota,
            aprovado=aprovado,
            arquivo_origem=str(pdf_path),
            usuario=usuario,
        )
