"""Domain enums following Spec.md section 3.6 and 2.3"""
from enum import StrEnum


class AnalysisStatus(StrEnum):
    RASCUNHO = "rascunho"
    PROCESSANDO = "processando"
    PENDENTE_DADOS = "pendente_dados"
    NAO_ATENDE_TECNICAMENTE = "nao_atende_tecnicamente"
    PRE_APROVAVEL_TECNICAMENTE = "pre_aprovavel_tecnicamente"
    PENDENTE_CERTIFICACAO = "pendente_certificacao"
    CERTIFICADA = "certificada"
    CERTIFICADA_COM_RESSALVAS = "certificada_com_ressalvas"
    INDEFERIDA = "indeferida"
    COMPLEMENTACAO_SOLICITADA = "complementacao_solicitada"


class DecisaoStatus(StrEnum):
    DEFERIDA = "deferida"
    INDEFERIDA = "indeferida"
    COMPLEMENTACAO = "complementacao"


class TipoPrograma(StrEnum):
    UFSM = "ufsm"
    EXTERNO = "externo"


class MatchClassification(StrEnum):
    EQUIVALENTE = "equivalente"
    PARCIALMENTE_EQUIVALENTE = "parcialmente_equivalente"
    AUSENTE = "ausente"


class UserRole(StrEnum):
    ADMIN = "admin"
    COORDENACAO = "coordenacao"
    SECRETARIA = "secretaria"
    CONSULTA = "consulta"


class CargoHorariaFonte(StrEnum):
    EXTRAIDA_PDF = "extraida_pdf"
    EXTRAIDA_TEXTO = "extraida_texto"
    MANUAL = "manual"
    CADASTRO_UFSM = "cadastro_ufsm"
    MANUAL_IMPORTACAO = "manual_importacao"
