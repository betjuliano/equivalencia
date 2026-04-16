"""Infrastructure — NLP Comparator engine (Spec.md section 7)

Score = 0.55 * cosine_tfidf + 0.20 * overlap_keywords + 0.15 * ngram_similarity + 0.10 * synonym_bonus
Thresholds: >= 0.75 = equivalente, >= 0.45 = parcialmente equivalente, < 0.45 = ausente
"""
from __future__ import annotations
import re
import math
import logging
from typing import List, Dict, Optional, Tuple, Set
from collections import Counter
from src.domain.enums import MatchClassification
from src.domain.analysis import MatchItem

logger = logging.getLogger(__name__)

# ─── Portuguese stopwords ────────────────────────────────────────────────────
STOPWORDS: Set[str] = {
    "a", "o", "e", "é", "em", "de", "do", "da", "dos", "das", "no", "na",
    "nos", "nas", "por", "para", "com", "sem", "que", "se", "ao", "às",
    "um", "uma", "uns", "umas", "os", "as", "ou", "mas", "como", "mais",
    "ser", "ter", "seu", "sua", "seus", "suas", "este", "esta", "esse", "essa",
    "pelo", "pela", "pelos", "pelas", "entre", "sobre", "sob", "ante",
    "foi", "são", "tem", "teve", "era", "não", "quando", "muito", "bem",
    "após", "até", "aqui", "isso", "ele", "ela", "eles", "elas",
}

# ─── Expanded synonym dictionary (Portuguese academic/ADM terms) ──────────────
SYNONYMS: Dict[str, List[str]] = {
    # Contabilidade / Finanças
    "contábil": ["contabilidade", "balanço", "demonstrações", "ativo", "passivo",
                 "resultado", "patrimonial", "balancete"],
    "contabilidade": ["contábil", "demonstrações contábeis", "balanço patrimonial",
                      "resultado do exercício"],
    "auditoria": ["perícia", "controle interno", "compliance", "fiscalização", "revisão"],
    "custos": ["custeio", "custo", "gestão de custos", "análise de custos",
               "custo estratégico", "custeio variável", "custeio por absorção"],
    "financeiro": ["finanças", "econômico", "monetário", "orçamento", "fluxo de caixa",
                   "capital", "liquidez", "rentabilidade", "retorno", "avaliação financeira"],
    "finanças": ["financeiro", "gestão financeira", "análise financeira", "orçamentário",
                 "investimentos", "mercado financeiro"],
    "orçamento": ["orçamentário", "planejamento financeiro", "budget", "controle orçamentário"],
    "investimento": ["aplicação", "ativo financeiro", "retorno", "risco", "portfólio",
                     "análise de investimentos", "mercado de capitais"],
    "mercado de capitais": ["bolsa de valores", "ações", "títulos", "debêntures",
                            "fundos de investimento", "renda variável"],
    "matemática financeira": ["juros", "capitalização", "desconto", "amortização",
                              "equivalência de capitais", "taxa de juros"],

    # Direito
    "tributário": ["fiscal", "tributação", "imposto", "contribuição", "tributo",
                   "direito tributário", "obrigação tributária"],
    "direito": ["legislação", "lei", "norma", "jurídico", "legal", "normativo",
                "ordenamento jurídico"],
    "trabalhista": ["direito do trabalho", "relações de trabalho", "clt", "emprego",
                    "vínculo empregatício", "relações trabalhistas"],
    "empresarial": ["direito empresarial", "sociedades", "comercial", "negócios jurídicos",
                    "contratos empresariais"],
    "ética": ["filosófico", "moral", "deontologia", "responsabilidade social",
              "valores organizacionais", "conduta"],

    # Administração geral
    "administrativo": ["gestão", "administração", "gerencial", "management"],
    "administração": ["gestão", "governança", "management", "gerenciamento", "organização"],
    "planejamento": ["estratégia", "plano", "programação", "formulação estratégica",
                     "planejamento estratégico", "controle"],
    "estratégia": ["estratégico", "planejamento estratégico", "vantagem competitiva",
                   "posicionamento estratégico", "análise estratégica"],
    "processos": ["processo", "fluxo de trabalho", "workflow", "gestão de processos",
                  "bpm", "mapeamento de processos", "modelagem"],
    "qualidade": ["gestão da qualidade", "controle de qualidade", "melhoria contínua",
                  "iso", "six sigma", "kaizen", "padronização"],
    "inovação": ["criatividade", "desenvolvimento", "empreendedorismo", "startup",
                 "novos produtos", "gestão da inovação"],
    "empreendedorismo": ["empreendedor", "startup", "inovação", "novo negócio", "plano de negócios"],

    # Marketing
    "marketing": ["mercadologia", "consumidor", "mercado", "comercial", "publicidade",
                  "propaganda", "vendas", "marca", "produto"],
    "consumidor": ["comportamento do consumidor", "cliente", "demanda", "necessidade",
                   "satisfação", "fidelização"],
    "vendas": ["comercial", "força de vendas", "varejo", "distribuição", "canal de vendas"],
    "marca": ["brand", "branding", "identidade de marca", "imagem de marca", "posicionamento"],

    # Recursos Humanos / Pessoas
    "gestão de pessoas": ["recursos humanos", "capital humano", "rh", "gestão de rh",
                          "pessoas", "equipes"],
    "recursos humanos": ["gestão de pessoas", "capital humano", "rh", "seleção",
                         "treinamento", "desenvolvimento"],
    "treinamento": ["desenvolvimento", "capacitação", "formação", "aprendizagem organizacional",
                    "educação corporativa"],
    "liderança": ["líder", "gestão de equipes", "motivação", "comportamento organizacional",
                  "chefia", "supervisão"],
    "comportamento organizacional": ["comportamento humano", "motivação", "cultura",
                                     "clima organizacional", "dinâmica de grupo"],
    "remuneração": ["salário", "cargos e salários", "benefícios", "compensação",
                    "política salarial", "carreiras"],

    # Logística / Operações / Produção
    "logística": ["cadeia de suprimentos", "supply chain", "distribuição", "transporte",
                  "armazenagem", "estoque", "gestão de estoques"],
    "produção": ["operações", "manufatura", "planejamento da produção", "pcp",
                 "gestão da produção", "organização da produção"],
    "materiais": ["administração de materiais", "compras", "suprimentos", "estoque",
                  "patrimônio", "almoxarifado"],

    # Quantitativas / Matemática / Estatística
    "estatística": ["probabilidade", "análise quantitativa", "dados", "inferência",
                    "amostragem", "regressão", "estatística descritiva"],
    "matemática": ["cálculo", "álgebra", "análise matemática", "quantitativo",
                   "matemática aplicada"],
    "cálculo": ["matemática", "derivada", "integral", "análise matemática", "cálculo diferencial"],
    "pesquisa": ["metodologia", "método científico", "pesquisa científica", "análise de dados",
                 "levantamento", "survey"],

    # Sistemas de Informação / TI
    "sistemas de informação": ["tecnologia da informação", "ti", "sistema", "software",
                               "informática", "erp", "banco de dados"],
    "programação": ["algoritmo", "software", "desenvolvimento", "código", "computação"],
    "banco de dados": ["sgbd", "sql", "dados relacionais", "base de dados"],
    "tecnologia": ["ti", "digital", "inovação tecnológica", "transformação digital",
                   "computação", "sistema"],

    # Economia
    "economia": ["microeconomia", "macroeconomia", "teoria econômica", "econômico"],
    "microeconomia": ["mercados", "demanda", "oferta", "preços", "concorrência",
                      "estrutura de mercado"],
    "macroeconomia": ["pib", "inflação", "política econômica", "economia nacional",
                      "balança comercial"],

    # Administração pública / Social
    "administração pública": ["gestão pública", "setor público", "governo", "políticas públicas",
                              "administração governamental"],
    "sustentabilidade": ["ambiental", "social", "esg", "responsabilidade socioambiental",
                         "desenvolvimento sustentável", "tripé da sustentabilidade"],

    # Psicologia / Sociologia / Filosofia
    "psicologia": ["comportamento", "motivação", "percepção", "psicologia aplicada",
                   "saúde mental", "bem-estar"],
    "sociologia": ["sociedade", "organizações sociais", "análise social", "cultura",
                   "relações sociais", "estrutura social"],
    "filosofia": ["ética", "epistemologia", "pensamento crítico", "moral",
                  "filosofia organizacional"],
}


def _tokenize(text: str) -> List[str]:
    """Tokenize text, removing stopwords. Returns [] on None or non-string input."""
    if not text or not isinstance(text, str):
        return []
    try:
        tokens = re.sub(r"[^a-záéíóúâêîôûãõàèìòùç\s]", " ", text.lower())
        return [t for t in tokens.split() if t and t not in STOPWORDS and len(t) > 2]
    except Exception:
        return []


def _ngrams(tokens: List[str], n: int) -> List[str]:
    if not tokens or len(tokens) < n:
        return []
    return [" ".join(tokens[i: i + n]) for i in range(len(tokens) - n + 1)]


def _tfidf_vectors(corpus: List[List[str]]) -> List[Dict[str, float]]:
    """Compute TF-IDF vectors for a corpus of tokenized documents."""
    if not corpus:
        return []
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
    if not v1 or not v2:
        return 0.0
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
    if not t1 or not t2:
        return False
        
    def _match(word: str, token_list: List[str]) -> bool:
        """True se a palavra raiz ou token existir substancialmente no outro."""
        w = word.lower()
        if len(w) > 4:
            w = w[:-1] # Remove última letra (a/o/s) p/ match parcial
        
        for t in token_list:
            if w in t or t in word.lower():
                return True
        return False

    for word, syns in SYNONYMS.items():
        if not word or not syns:
            continue
            
        # If the root word is in t1, check if any synonym is in t2
        if _match(word, t1):
            for syn in syns:
                if syn and _match(syn, t2):
                    return True
                    
        # Reverse: if any synonym is in t1, check if root word is in t2
        for syn in syns:
            if syn and _match(syn, t1):
                if _match(word, t2):
                    return True
                    
    return False


def _classify(score: float) -> Tuple[MatchClassification, float]:
    if score >= 0.75:
        return MatchClassification.EQUIVALENTE, 1.0
    elif score >= 0.45:
        return MatchClassification.PARCIALMENTE_EQUIVALENTE, 0.5
    else:
        return MatchClassification.AUSENTE, 0.0


# Configurable weights (Tuned for structured topic comparisons)
WEIGHTS = {
    "cosine_tfidf": 0.45,
    "overlap_keywords": 0.30,
    "ngram_similarity": 0.10,
    "synonym_bonus": 0.15,
}


def compare_programs(ufsm_items: List[str], external_items: List[str]) -> List[MatchItem]:
    """Compare each UFSM item against all external items and return match results.

    Robust against empty lists, None values, whitespace-only strings, and
    unexpected exceptions in individual comparisons.
    """
    # Filter out None and blank strings
    ufsm_items = [t for t in (ufsm_items or []) if t and isinstance(t, str) and t.strip()]
    external_items = [t for t in (external_items or []) if t and isinstance(t, str) and t.strip()]

    if not ufsm_items or not external_items:
        return []

    try:
        # Build tokenized corpus for TF-IDF
        all_texts = ufsm_items + external_items
        corpus = [_tokenize(t) for t in all_texts]
        vectors = _tfidf_vectors(corpus)

        ufsm_vecs = vectors[: len(ufsm_items)]
        ext_vecs = vectors[len(ufsm_items):]
        ext_tokens = [_tokenize(t) for t in external_items]
    except Exception as exc:
        logger.error("compare_programs: failed to build TF-IDF corpus: %s", exc)
        return []

    results: List[MatchItem] = []

    for i, (ufsm_text, ufsm_vec) in enumerate(zip(ufsm_items, ufsm_vecs)):
        try:
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
        except Exception as exc:
            logger.warning(
                "compare_programs: error processing item %d (%r): %s", i, ufsm_text, exc
            )
            # Append a safe fallback item instead of crashing
            results.append(
                MatchItem(
                    ufsm_item=ufsm_text,
                    externo_item=None,
                    score_bruto=0.0,
                    score_final=0.0,
                    palavras_coincidentes=[],
                    bonus_sinonimos=False,
                    classificacao=MatchClassification.AUSENTE,
                    pontuacao=0.0,
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
    if not ufsm_ch or not ext_ch or ufsm_ch <= 0 or ext_ch <= 0:
        return 0.0
    return round(min(ufsm_ch, ext_ch) / max(ufsm_ch, ext_ch) * 100, 2)
