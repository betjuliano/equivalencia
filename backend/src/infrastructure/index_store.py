"""Infrastructure — Index store for the 5 index JSON files (Spec.md section 4.3-4.4)"""
from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
from .file_store import write_json_atomic, read_json, read_json_sync


class IndexStore:
    def __init__(self, data_dir: Path):
        self.data_dir = Path(data_dir)
        self.index_dir = self.data_dir / "index"

    def _path(self, name: str) -> Path:
        return self.index_dir / name

    async def _load(self, name: str) -> Dict:
        data = await read_json(self._path(name))
        return data or {}

    async def _save(self, name: str, data: Dict) -> None:
        data["updated_at"] = datetime.now(timezone.utc).isoformat()
        await write_json_atomic(self._path(name), data)

    # ── Programs UFSM ──────────────────────────────────────────────────────
    async def add_ufsm_program(self, entry: Dict) -> None:
        idx = await self._load("index_programas_ufsm.json")
        items: List = idx.get("items", [])
        items = [i for i in items if i.get("id") != entry["id"]]
        items.append(entry)
        await self._save("index_programas_ufsm.json", {"version": "1.0", "items": items})

    async def search_ufsm_programs(self, curso: Optional[str] = None, query: Optional[str] = None) -> List[Dict]:
        idx = await self._load("index_programas_ufsm.json")
        items: List = idx.get("items", [])
        if curso:
            items = [i for i in items if curso.lower() in i.get("curso_slug", "").lower()]
        if query:
            q = query.lower()
            items = [i for i in items if q in i.get("nome", "").lower() or q in i.get("codigo", "").lower()]
        return items

    # ── Programs Externos ──────────────────────────────────────────────────
    async def add_external_program(self, entry: Dict) -> None:
        idx = await self._load("index_programas_externos.json")
        items: List = idx.get("items", [])
        items = [i for i in items if i.get("id") != entry["id"]]
        items.append(entry)
        await self._save("index_programas_externos.json", {"version": "1.0", "items": items})

    async def search_external_programs(self, instituicao: Optional[str] = None, query: Optional[str] = None) -> List[Dict]:
        idx = await self._load("index_programas_externos.json")
        items: List = idx.get("items", [])
        if instituicao:
            items = [i for i in items if instituicao.lower() in i.get("instituicao_slug", "").lower()]
        if query:
            q = query.lower()
            items = [i for i in items if q in i.get("nome", "").lower()]
        return items

    # ── Analises ───────────────────────────────────────────────────────────
    async def add_analise(self, entry: Dict) -> None:
        idx = await self._load("index_analises.json")
        items: List = idx.get("items", [])
        items = [i for i in items if i.get("id") != entry["id"]]
        items.append(entry)
        await self._save("index_analises.json", {"version": "1.0", "items": items})

    async def search_reusable_analyses(self, ufsm_program_id: str, external_query: Optional[str] = None) -> List[Dict]:
        idx = await self._load("index_analises.json")
        items: List = idx.get("items", [])
        items = [i for i in items if i.get("ufsm_program_id") == ufsm_program_id]
        if external_query:
            q = external_query.lower()
            items = [i for i in items if q in i.get("external_program_id", "").lower()]
        return items

    # ── Certificações ──────────────────────────────────────────────────────
    async def add_certificacao(self, entry: Dict) -> None:
        idx = await self._load("index_certificacoes.json")
        items: List = idx.get("items", [])
        items = [i for i in items if i.get("id") != entry["id"]]
        items.append(entry)
        await self._save("index_certificacoes.json", {"version": "1.0", "items": items})

    # ── Consulta pública ───────────────────────────────────────────────────
    async def upsert_consulta_publica(self, entry: Dict) -> None:
        idx = await self._load("index_consulta_publica.json")
        items: List = idx.get("items", [])
        items = [i for i in items if i.get("certificacao_id") != entry["certificacao_id"]]
        items.append(entry)
        await self._save("index_consulta_publica.json", {"version": "1.0", "items": items})

    async def search_consulta_publica(self, curso: Optional[str] = None, disciplina: Optional[str] = None) -> List[Dict]:
        idx = await self._load("index_consulta_publica.json")
        items: List = idx.get("items", [])
        items = [i for i in items if i.get("status") == "certificada"]
        if curso:
            items = [i for i in items if curso.lower() in i.get("curso_slug", "").lower()]
        if disciplina:
            d = disciplina.lower()
            items = [i for i in items if d in i.get("disciplina_codigo", "").lower() or d in i.get("disciplina_nome", "").lower()]
        return items
