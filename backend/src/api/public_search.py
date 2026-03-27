"""API — Public search endpoint (Spec.md section 10.13, F09)"""
from __future__ import annotations
from typing import Optional
from fastapi import APIRouter, Depends
from src.infrastructure.index_store import IndexStore

router = APIRouter()


def get_index_store() -> IndexStore:
    from src.main import index_store
    return index_store


@router.get("/public/equivalences")
async def search_public_equivalences(
    curso: Optional[str] = None,
    disciplina: Optional[str] = None,
    idx: IndexStore = Depends(get_index_store),
):
    items = await idx.search_consulta_publica(curso=curso, disciplina=disciplina)
    return {"items": items}
