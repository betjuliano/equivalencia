"""Infrastructure — NLP Comparator engine (Spec.md section 7)

Arquivo a atualizar: comparator.py

Score = 0.55 * cosine_tfidf + 0.20 * overlap_keywords + 0.15 * ngram_similarity + 0.10 * synonym_bonus
Thresholds: >= 0.75 = equivalente, >= 0.45 = parcialmente equivalente, < 0.45 = ausente
"""
from __future__ import annotations
import re
import math
from typing import List, Dict, Optional, Tuple, Set
from collections import Counter
from src.domain.enums import MatchClassification
from src.domain.analysis import MatchItem

# ─── Portuguese stopwords (minimal set) ─────────────────────────────────────
STOPWORDS: Set[str] = {
    "a", "o", "e", "é", "em", "de", "do", "da", "dos", "das", "no", "na",
    "nos", "nas", "por", "para", "com", "sem", "que", "se", "ao", "às",
    "um", "uma", "uns", "umas", "os", "as", "ou", "mas", "como", "mais",
    "ser", "ter", "seu", "sua", "seus", "suas", "este", "esta", "esse", "essa",
    "pelo", "pela", "pelos", "pelas", "entre", "sobre", "sob", "ante",
}

# ─── Basic synonym dictionary (Portuguese academic terms) ───────────────────
SYNONYMS: Dict[str, List[str]] = {
    "tributário": ["fiscal", "tributação", "imposto", "contribuição"],
    "direito": ["legislação", "lei", "norma", "jurídico"],
    "administrativo": ["gestão", "administração", "gerencial"],
    "contábil": ["contabilidade", "balanço", "demonstrações"],
    "financeiro": ["finanças", "financeiro", "econômico", "monetário"],
    "marketing": ["mercadologia", "consumidor", "mercado", "comercial"],
    "estatística": ["probabilidade", "análise quantitativa", "dados"],
    "cálculo": ["matemática", "álgebra", "derivada", "integral"],
    "programação": ["algoritmo", "software", "desenvolvimento", "código"],
    "banco de dados": ["sgbd", "sql", "dados relacionais"],
}


def _tokenize(text: str) -> List[str]:
    tokens = re.sub(r"[^a-záéíóúâêîôûãõàèìòùç\s]", " ", text.lower())
    return [t for t in tokens.split() if t and t not in STOPWORDS and len(t) > 2]


def _ngrams(tokens: List[str], n: int) -> List[str]:
    return [" ".join(tokens[i: i + n]) for i in range(len(tokens) - n + 1)]


def _tfidf_vectors(corpus: List[List[str]]) -> List[Dict[str, float]]:
    """Compute TF-IDF vectors for a corpus of tokenized documents."""
    N = len(corpus)
    df: Dict[str, int] = Counter()
    for tokens in corpus:
        for t in set(tokens):
            df[t] += 1

    vectors = []
    for tokens in corpus:
        tf = Counter(tokens)
        total = len(tokens) or 1
        vec: Dict[str, float] = {}
        for term, count in tf.items():
            idf = math.log((N + 1) / (df[term] + 1)) + 1
            vec[term] = (count / total) * idf
        vectors.append(vec)
    return vectors


def _cosine(v1: Dict[str, float], v2: Dict[str, float]) -> float:
    common = set(v1) & set(v2)
    if not common:
        return 0.0
    dot = sum(v1[k] * v2[k] for k in common)
    n1 = math.sqrt(sum(x * x for x in v1.values()))
    n2 = math.sqrt(sum(x * x for x in v2.values()))
    if n1 == 0 or n2 == 0:
        return 0.0
    return dot / (n1 * n2)


def _keyword_overlap(t1: List[str], t2: List[str]) -> float:
    s1, s2 = set(t1), set(t2)
    if not s1 or not s2:
        return 0.0
    return len(s1 & s2) / max(len(s1), len(s2))


def _ngram_similarity(t1: List[str], t2: List[str], n: int = 2) -> float:
    ng1 = set(_ngrams(t1, n))
    ng2 = set(_ngrams(t2, n))
    if not ng1 or not ng2:
        return 0.0
    return len(ng1 & ng2) / max(len(ng1), len(ng2))


def _synonym_bonus(t1: List[str], t2: List[str]) -> bool:
    s2 = set(t2)
    for word, syns in SYNONYMS.items():
        if word in " ".join(t1):
            for syn in syns:
                if syn in " ".join(t2):
                    return True
    return False


def _classify(score: float) -> Tuple[MatchClassification, float]:
    if score >= 0.75:
        return MatchClassification.EQUIVALENTE, 1.0
    elif score >= 0.45:
        return MatchClassification.PARCIALMENTE_EQUIVALENTE, 0.5
    else:
        return MatchClassification.AUSENTE, 0.0


# Configurable weights
WEIGHTS = {
    "cosine_tfidf": 0.55,
    "overlap_keywords": 0.20,
    "ngram_similarity": 0.15,
    "synonym_bonus": 0.10,
}


def compare_programs(ufsm_items: List[str], external_items: List[str]) -> List[MatchItem]:
    """Compare each UFSM item against all external items and return match results."""
    if not ufsm_items or not external_items:
        return []

    # Build tokenized corpus for TF-IDF
    all_texts = ufsm_items + external_items
    corpus = [_tokenize(t) for t in all_texts]
    vectors = _tfidf_vectors(corpus)

    ufsm_vecs = vectors[: len(ufsm_items)]
    ext_vecs = vectors[len(ufsm_items):]
    ext_tokens = [_tokenize(t) for t in external_items]

    results: List[MatchItem] = []

    for i, (ufsm_text, ufsm_vec) in enumerate(zip(ufsm_items, ufsm_vecs)):
        ufsm_tok = _tokenize(ufsm_text)
        best_score = -1.0
        best_j = 0
        best_raw: Dict = {}

        for j, (ext_text, ext_vec) in enumerate(zip(external_items, ext_vecs)):
            ext_tok = ext_tokens[j]
            cos = _cosine(ufsm_vec, ext_vec)
            overlap = _keyword_overlap(ufsm_tok, ext_tok)
            ngram = _ngram_similarity(ufsm_tok, ext_tok)
            bonus = _synonym_bonus(ufsm_tok, ext_tok)
            bonus_val = WEIGHTS["synonym_bonus"] if bonus else 0.0

            score = (
                WEIGHTS["cosine_tfidf"] * cos
                + WEIGHTS["overlap_keywords"] * overlap
                + WEIGHTS["ngram_similarity"] * ngram
                + bonus_val
            )
            if score > best_score:
                best_score = score
                best_j = j
                best_raw = {
                    "cos": cos, "overlap": overlap, "ngram": ngram,
                    "bonus": bonus, "ext_tok": ext_tok,
                }

        classification, pontuacao = _classify(best_score)
        common_words = sorted(set(ufsm_tok) & set(best_raw.get("ext_tok", [])))

        results.append(
            MatchItem(
                ufsm_item=ufsm_text,
                externo_item=external_items[best_j] if best_score >= 0 else None,
                score_bruto=round(best_raw.get("cos", 0.0), 4),
                score_final=round(best_score, 4),
                palavras_coincidentes=common_words[:10],
                bonus_sinonimos=best_raw.get("bonus", False),
                classificacao=classification,
                pontuacao=pontuacao,
            )
        )

    return results


def calculate_content_score(matches: List[MatchItem]) -> float:
    """Spec formula: (sum of pontuacoes / total items) * 100"""
    if not matches:
        return 0.0
    return round(sum(m.pontuacao for m in matches) / len(matches) * 100, 2)


def calculate_workload_score(ufsm_ch: float, ext_ch: float) -> float:
    """Spec formula: (min / max) * 100"""
    if ufsm_ch <= 0 or ext_ch <= 0:
        return 0.0
    return round(min(ufsm_ch, ext_ch) / max(ufsm_ch, ext_ch) * 100, 2)
