"""Infrastructure — Structural Parser for program text (Spec.md section 6)

Pipeline:
1. Read input
2. Normalize encoding UTF-8
3. Remove duplicate whitespace
4. Standardize line breaks
5. Identify sections (units, topics, subtopics)
6. Build hierarchical tree
7. Extract workload
8. Extract bibliography
9. Return structured JSON
"""
from __future__ import annotations
import re
from typing import Optional, List, Tuple
from src.domain.program import (
    ProgramaEstruturado, Unidade, Topico, Subtopico, Bibliografia, CargoHorariaFonte
)
from src.domain.enums import CargoHorariaFonte as CHFonte


# ─── Regex patterns ─────────────────────────────────────────────────────────

UNIDADE_RE = re.compile(
    r"^\s*(?:UNIDADE\s+TEMÁTICA\s+|UNIDADE\s+|MÓDULO\s+)(\w+)[:\s–-]*(.*)?$",
    re.IGNORECASE | re.MULTILINE,
)
TOPICO_RE = re.compile(r"^\s*(\d+\.\d+)\s+(.+)$", re.MULTILINE)
SUBTOPICO_RE = re.compile(r"^\s*(\d+\.\d+\.\d+)\s+(.+)$", re.MULTILINE)

BIBLIO_START_RE = re.compile(
    r"^\s*(REFERÊNCIAS|BIBLIOGRAFIA(?:\s+BÁSICA)?(?:\s+COMPLEMENTAR)?)[\s:]*$",
    re.IGNORECASE | re.MULTILINE,
)
BIBLIO_COMP_RE = re.compile(r"COMPLEMENTAR", re.IGNORECASE)

CH_RE = re.compile(
    r"(?:Carga\s+Hor[aá]ria|CH|horas?\-?aula|h/a)\s*:?\s*(\d+(?:[.,]\d+)?)\s*(?:h|horas?|h/a|h\.a\.)?",
    re.IGNORECASE,
)
CH_INLINE_RE = re.compile(r"\b(\d+)\s*(?:h|horas?|h/a)\b", re.IGNORECASE)


def _normalize(text: str) -> str:
    """Normalize text: UTF-8, collapse whitespace, standardize newlines."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Collapse multiple blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Collapse multiple spaces (but not newlines)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def extract_workload(text: str) -> Tuple[Optional[float], CHFonte]:
    """Try to extract workload hours from text."""
    m = CH_RE.search(text)
    if m:
        val = float(m.group(1).replace(",", "."))
        return val, CHFonte.EXTRAIDA_TEXTO
    m = CH_INLINE_RE.search(text)
    if m:
        return float(m.group(1)), CHFonte.EXTRAIDA_TEXTO
    return None, CHFonte.MANUAL


def extract_bibliography(text: str) -> Tuple[List[str], List[str]]:
    """Extract basic and complementary bibliography sections."""
    basica: List[str] = []
    complementar: List[str] = []

    sections = BIBLIO_START_RE.split(text)
    if len(sections) < 2:
        return basica, complementar

    in_comp = False
    current: List[str] = []

    for i, sect in enumerate(sections):
        if i == 0:
            continue
        # sections alternates: header text, content, header text, content...
        if i % 2 == 1:
            in_comp = bool(BIBLIO_COMP_RE.search(sect))
            continue
        lines = [ln.strip() for ln in sect.strip().split("\n") if ln.strip()]
        refs = [ln for ln in lines if ln and not BIBLIO_START_RE.match(ln)]
        if in_comp:
            complementar.extend(refs)
        else:
            basica.extend(refs)

    return basica, complementar


def parse_program(text: str) -> Tuple[ProgramaEstruturado, Optional[float], CHFonte, str]:
    """
    Parse raw program text into structured form.
    Returns: (ProgramaEstruturado, carga_horaria, fonte_carga_horaria, estrutura_flag)
    estrutura_flag: 'completa' | 'parcial'
    """
    text = _normalize(text)

    carga, fonte = extract_workload(text)
    basica, complementar = extract_bibliography(text)

    # Split into content / bibliography sections
    bib_match = BIBLIO_START_RE.search(text)
    content_text = text[: bib_match.start()] if bib_match else text

    unidades: List[Unidade] = []
    unidade_boundaries = list(UNIDADE_RE.finditer(content_text))

    def _extract_topicos(block: str) -> List[Topico]:
        topicos: List[Topico] = []
        sub_matches = list(SUBTOPICO_RE.finditer(block))
        top_matches = list(TOPICO_RE.finditer(block))

        for tm in top_matches:
            num = tm.group(1)
            txt = tm.group(2).strip()
            subs = [
                Subtopico(numero=sm.group(1), texto=sm.group(2).strip())
                for sm in sub_matches
                if sm.group(1).startswith(num + ".")
            ]
            topicos.append(Topico(numero=num, texto=txt, subtopicos=subs))
        return topicos

    if unidade_boundaries:
        for i, um in enumerate(unidade_boundaries):
            start = um.end()
            end = unidade_boundaries[i + 1].start() if i + 1 < len(unidade_boundaries) else len(content_text)
            block = content_text[start:end]
            topicos = _extract_topicos(block)
            unidades.append(
                Unidade(
                    numero=um.group(1),
                    titulo=um.group(2).strip() if um.group(2) else f"Unidade {um.group(1)}",
                    topicos=topicos,
                )
            )
        flag = "completa"
    else:
        # No units found — try flat topic extraction
        topicos = _extract_topicos(content_text)
        if topicos:
            unidades.append(Unidade(numero="1", titulo="Conteúdo Programático", topicos=topicos))
            flag = "parcial"
        else:
            # Fallback: treat each non-empty line as a topic
            lines = [ln.strip() for ln in content_text.split("\n") if ln.strip() and len(ln.strip()) > 5]
            topicos = [Topico(numero=str(i + 1), texto=ln) for i, ln in enumerate(lines[:50])]
            unidades.append(Unidade(numero="1", titulo="Conteúdo Programático", topicos=topicos))
            flag = "parcial"

    return (
        ProgramaEstruturado(unidades=unidades),
        carga,
        fonte,
        flag,
    )


def collect_items(estruturado: ProgramaEstruturado) -> List[str]:
    """Flatten the structured program into a list of comparable text items."""
    items: List[str] = []
    for u in estruturado.unidades:
        if u.titulo:
            items.append(u.titulo)
        for t in u.topicos:
            items.append(t.texto)
            for s in t.subtopicos:
                items.append(s.texto)
    return items
