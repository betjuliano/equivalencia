"""Domain models — Program (UFSM and External) following Spec.md section 5.1 and 5.2"""
from __future__ import annotations
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from .enums import TipoPrograma, CargoHorariaFonte


class Subtopico(BaseModel):
    numero: str
    texto: str


class Topico(BaseModel):
    numero: str
    texto: str
    subtopicos: List[Subtopico] = []


class Unidade(BaseModel):
    numero: str
    titulo: str
    topicos: List[Topico] = []


class ProgramaEstruturado(BaseModel):
    unidades: List[Unidade] = []


class Bibliografia(BaseModel):
    basica: List[str] = []
    complementar: List[str] = []


class MetadadosPrograma(BaseModel):
    versao_ppc: Optional[str] = None
    origem_importacao: str
    arquivo_origem: Optional[str] = None
    criado_em: str
    atualizado_em: str


class ProgramaUFSM(BaseModel):
    id: str
    tipo: TipoPrograma = TipoPrograma.UFSM
    codigo: str
    nome: str
    slug: str
    curso: str
    curso_slug: str
    carga_horaria: Optional[float] = None
    carga_horaria_fonte: Optional[CargoHorariaFonte] = None
    modalidade: str = "presencial"
    possui_extensao: bool = False
    e_estagio: bool = False
    e_tcc: bool = False
    programa_original: str = ""
    programa_estruturado: ProgramaEstruturado = Field(default_factory=ProgramaEstruturado)
    bibliografia: Bibliografia = Field(default_factory=Bibliografia)
    metadados: MetadadosPrograma


class ProgramaExterno(BaseModel):
    id: str
    tipo: TipoPrograma = TipoPrograma.EXTERNO
    codigo: str
    nome: str
    instituicao: str
    instituicao_slug: str
    curso_origem: str
    carga_horaria: Optional[float] = None
    carga_horaria_fonte: Optional[CargoHorariaFonte] = None
    modalidade: str = "presencial"
    nota: Optional[float] = None
    aprovado: Optional[bool] = None
    possui_extensao: bool = False
    e_estagio: bool = False
    e_tcc: bool = False
    programa_original: str = ""
    programa_estruturado: ProgramaEstruturado = Field(default_factory=ProgramaEstruturado)
    bibliografia: Bibliografia = Field(default_factory=Bibliografia)
    metadados: MetadadosPrograma
