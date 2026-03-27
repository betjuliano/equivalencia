# SPEC — Sistema de Comparação de Programas de Disciplinas (UFSM)

Documento técnico e funcional completo para desenvolvimento de um sistema web de apoio à análise de equivalência de disciplinas, aderente à Resolução UFSM nº 209/2025, com persistência local em arquivos `.json`, reuso de análises anteriores, certificação pela Coordenação de Curso e consulta rápida de equivalências certificadas por estudantes.

---

# 1. ESCOPO E PRINCÍPIOS

## 1.1 Nome do sistema

Curriculum Equivalence Analyzer

## 1.2 Finalidade

Desenvolver um sistema web que permita:

* receber dois programas de disciplina por texto colado ou PDF;
* estruturar o conteúdo programático automaticamente;
* comparar conteúdo e carga horária;
* verificar aderência mínima de 75% em ambos os critérios;
* produzir análise técnica preliminar;
* permitir certificação formal pela Coordenação;
* armazenar programas, análises e certificações em arquivos `.json` locais;
* reaproveitar análises já realizadas;
* disponibilizar consulta rápida das equivalências certificadas para alunos.

## 1.3 Natureza da decisão

O sistema **não substitui a decisão institucional da Coordenação de Curso**. Ele é um sistema de apoio à decisão com rastreabilidade técnica. A certificação final é humana.

## 1.4 Base de validade

A lógica do sistema deve atender à Resolução UFSM nº 209/2025, especialmente no que diz respeito a:

* equivalência mínima de 75% em conteúdo;
* equivalência mínima de 75% em carga horária;
* necessidade de aprovação e nota mínima quando aplicável;
* papel decisório da Coordenação;
* restrições relativas a estágio, TCC, extensão e modalidade.

---

# 2. PRODUCT REQUIREMENTS DOCUMENT (PRD)

## 2.1 Problema de negócio

A análise de equivalência de disciplinas tende a ser:

* manual;
* demorada;
* heterogênea entre cursos e coordenações;
* pouco transparente para os estudantes;
* pouco reaproveitável quando casos parecidos reaparecem.

O sistema deve reduzir retrabalho e padronizar a análise preliminar, sem retirar a competência decisória da Coordenação.

## 2.2 Objetivos do produto

### Objetivos principais

* padronizar a análise técnica de equivalência;
* reduzir o tempo médio por análise;
* aumentar a consistência entre casos semelhantes;
* criar memória institucional de análises e certificações;
* facilitar a consulta de equivalências já certificadas.

### Objetivos secundários

* aumentar transparência para estudantes;
* permitir auditoria posterior;
* reduzir repetição de comparações já consolidadas;
* apoiar gestão acadêmica baseada em histórico.

## 2.3 Perfis de usuário

### Coordenação de Curso

Pode:

* consultar análises pendentes;
* abrir uma análise;
* revisar resultado técnico;
* certificar, rejeitar ou solicitar complementação;
* consultar certificações anteriores.

### Secretaria/apoio administrativo

Pode:

* cadastrar ou revisar programas UFSM;
* iniciar comparações;
* anexar documentos;
* preencher dados faltantes;
* organizar fluxo processual.

### Estudante

Pode:

* consultar equivalências certificadas por curso/disciplina;
* iniciar solicitação com envio de documentos, se essa função for habilitada;
* visualizar se já existe caso certificado semelhante.

### Professor parecerista (opcional)

Pode:

* emitir parecer técnico complementar;
* comentar análise;
* sugerir ajuste da classificação.

## 2.4 Funcionalidades principais

### F01 — Cadastro e ingestão de programas

* entrada por texto colado;
* entrada por PDF;
* normalização de conteúdo;
* armazenamento do texto estruturado em `.json`.

### F02 — Base UFSM local

* cadastro de disciplinas UFSM em arquivos `.json`;
* busca por código, nome e curso;
* reutilização automática quando a disciplina UFSM já existir.

### F03 — Base externa local

* cadastro de disciplinas externas em arquivos `.json`;
* organização por instituição;
* reutilização quando houver histórico semelhante.

### F04 — Comparação de conteúdo

* parser estrutural de unidades, tópicos e subtópicos;
* comparação via NLP clássico e regras heurísticas;
* classificação item a item.

### F05 — Comparação de carga horária

* extração automática;
* solicitação manual quando não identificada;
* cálculo percentual objetivo.

### F06 — Geração de análise técnica

* resultado quantitativo;
* justificativas por item;
* status preliminar.

### F07 — Certificação pela Coordenação

* fluxo formal de certificação;
* identificação do coordenador;
* registro da decisão;
* trilha de auditoria.

### F08 — Reuso de análises anteriores

* detecção de equivalências já analisadas;
* pré-preenchimento;
* exibição de certificadas semelhantes.

### F09 — Consulta pública/acadêmica rápida

* busca por curso UFSM;
* busca por disciplina UFSM;
* listagem de equivalências certificadas.

### F10 — Exportação

* relatório da análise em PDF;
* possibilidade de relatório DOCX em fase 2.

## 2.5 Critérios de sucesso do produto

* redução superior a 50% no tempo médio de análise preliminar;
* reaproveitamento de análises em pelo menos 40% dos casos repetidos;
* consulta rápida funcional para estudantes;
* rastreabilidade completa da certificação.

---

# 3. REGRAS DE NEGÓCIO

## 3.1 Regra principal de equivalência

Uma análise só poderá ser classificada como **tecnicamente pré-aprovável** se atender simultaneamente:

* equivalência de conteúdo >= 75%;
* equivalência de carga horária >= 75%.

## 3.2 Fórmula de conteúdo

```text
Equivalência de conteúdo = (soma das pontuações dos itens / total de itens analisados) * 100
```

## 3.3 Fórmula de carga horária

```text
Equivalência de carga horária = (menor carga horária / maior carga horária) * 100
```

## 3.4 Escala de pontuação por item

* equivalente = 1.0
* parcialmente equivalente = 0.5
* ausente = 0.0

## 3.5 Regras normativas complementares

O sistema deve prever campos e alertas para:

* aprovação na disciplina de origem;
* nota final;
* modalidade da disciplina;
* se a disciplina possui extensão;
* se é estágio;
* se é TCC;
* instituição de origem;
* observações sobre credenciamento da instituição, quando exigível.

## 3.6 Status possíveis da análise

* `rascunho`
* `processando`
* `pendente_dados`
* `nao_atende_tecnicamente`
* `pre_aprovavel_tecnicamente`
* `pendente_certificacao`
* `certificada`
* `certificada_com_ressalvas`
* `indeferida`
* `complementacao_solicitada`

---

# 4. PERSISTÊNCIA LOCAL EM JSON

## 4.1 Decisão arquitetural

O sistema **não utilizará banco relacional como mecanismo principal de persistência**. O armazenamento será feito em arquivos `.json` no diretório local da aplicação.

Essa escolha deve ser tratada como decisão explícita de arquitetura, adequada para:

* portabilidade;
* backup simples;
* inspeção manual;
* implantação institucional enxuta;
* baixo acoplamento com infraestrutura externa.

## 4.2 Estrutura de diretórios

```text
/app
  /data
    /ufsm
      /courses
      /disciplines
    /externos
      /institutions
      /disciplines
    /analises
    /certificacoes
    /index
    /logs
    /uploads
      /pdf
```

## 4.3 Convenções de nomenclatura

### Disciplina UFSM

```text
codigoDisciplina_nomeDisciplina.json
```

Exemplo:

```text
CAD123_direito_tributario.json
```

### Disciplina externa

```text
codigoOuSlug_nomeInstituicaoOrigem.json
```

Exemplo:

```text
dir_trib_ufabc.json
```

### Análise

```text
analise_<timestamp>_<hashcurto>.json
```

Exemplo:

```text
analise_20260325T154501Z_a82c19.json
```

### Certificação

```text
certificacao_<curso>_<codigoDisciplina>_<hashcurto>.json
```

Exemplo:

```text
certificacao_administracao_CAD123_72af1a.json
```

### Índices

```text
index_programas_ufsm.json
index_programas_externos.json
index_analises.json
index_certificacoes.json
index_consulta_publica.json
```

## 4.4 Motivação do índice local

Como a persistência é baseada em arquivos, o sistema deve manter **índices auxiliares** para evitar leitura exaustiva de todos os arquivos a cada busca.

## 4.5 Regras de escrita segura

Toda gravação de `.json` deve seguir fluxo atômico:

1. gerar conteúdo em memória;
2. escrever arquivo temporário `.tmp`;
3. validar JSON gerado;
4. renomear atomicamente para o nome final;
5. atualizar índices.

## 4.6 Lock de concorrência

Como múltiplos usuários podem operar simultaneamente, o backend deve implementar:

* lock por arquivo;
* lock por índice;
* fila simples de escrita;
* prevenção de corrupção por escrita concorrente.

No MVP, o lock pode ser por mutex em memória por caminho de arquivo. Em produção local multiworker, usar lock por arquivo no sistema operacional.

---

# 5. MODELO DE DADOS EM JSON

## 5.1 Programa UFSM

```json
{
  "id": "ufsm_CAD123",
  "tipo": "ufsm",
  "codigo": "CAD123",
  "nome": "Direito Tributário",
  "slug": "direito_tributario",
  "curso": "Administração",
  "curso_slug": "administracao",
  "carga_horaria": 60,
  "carga_horaria_fonte": "manual_importacao",
  "modalidade": "presencial",
  "possui_extensao": false,
  "e_estagio": false,
  "e_tcc": false,
  "programa_original": "texto bruto ou referência ao pdf",
  "programa_estruturado": {
    "unidades": []
  },
  "bibliografia": {
    "basica": [],
    "complementar": []
  },
  "metadados": {
    "versao_ppc": "2025",
    "origem_importacao": "cadastro_admin",
    "criado_em": "2026-03-25T15:45:01Z",
    "atualizado_em": "2026-03-25T15:45:01Z"
  }
}
```

## 5.2 Programa externo

```json
{
  "id": "ext_ufabc_direito_tributario",
  "tipo": "externo",
  "codigo": "DIRTRIB01",
  "nome": "Direito Tributário",
  "instituicao": "UFABC",
  "instituicao_slug": "ufabc",
  "curso_origem": "Administração Pública",
  "carga_horaria": 45,
  "carga_horaria_fonte": "extraida_pdf",
  "modalidade": "presencial",
  "nota": 7.5,
  "aprovado": true,
  "possui_extensao": false,
  "e_estagio": false,
  "e_tcc": false,
  "programa_original": "texto bruto ou referência ao pdf",
  "programa_estruturado": {
    "unidades": []
  },
  "bibliografia": {
    "basica": [],
    "complementar": []
  },
  "metadados": {
    "arquivo_origem": "uploads/pdf/arquivo.pdf",
    "origem_importacao": "envio_usuario",
    "criado_em": "2026-03-25T15:45:01Z",
    "atualizado_em": "2026-03-25T15:45:01Z"
  }
}
```

## 5.3 Análise

```json
{
  "id": "analise_20260325T154501Z_a82c19",
  "ufsm_program_id": "ufsm_CAD123",
  "external_program_id": "ext_ufabc_direito_tributario",
  "threshold_content": 75,
  "threshold_workload": 75,
  "content_score": 81.25,
  "workload_score": 75.00,
  "resultado_tecnico": "pre_aprovavel_tecnicamente",
  "resultado_final": "pendente_certificacao",
  "reused_from_analysis_id": null,
  "workload": {
    "ufsm": 60,
    "externo": 45,
    "fonte_ufsm": "cadastro_ufsm",
    "fonte_externo": "extraida_pdf"
  },
  "matches": [],
  "alertas": [],
  "observacoes_tecnicas": "Texto explicativo",
  "metadados": {
    "criado_por": "user_001",
    "criado_em": "2026-03-25T15:45:01Z",
    "algoritmo_versao": "1.0.0"
  }
}
```

## 5.4 Certificação

```json
{
  "id": "certificacao_administracao_CAD123_72af1a",
  "analysis_id": "analise_20260325T154501Z_a82c19",
  "curso": "Administração",
  "curso_slug": "administracao",
  "disciplina_ufsm_codigo": "CAD123",
  "disciplina_ufsm_nome": "Direito Tributário",
  "instituicao_origem": "UFABC",
  "disciplina_origem_nome": "Direito Tributário",
  "status": "certificada",
  "decisao": "deferida",
  "coordenador": {
    "nome": "Nome do Coordenador",
    "email": "coord@ufsm.br",
    "user_id": "coord_001"
  },
  "ressalvas": null,
  "data_certificacao": "2026-03-25T16:10:00Z",
  "ativo": true,
  "publicavel_para_consulta": true
}
```

## 5.5 Índice de consulta pública

```json
{
  "version": "1.0",
  "updated_at": "2026-03-25T16:10:00Z",
  "items": [
    {
      "curso_slug": "administracao",
      "curso": "Administração",
      "disciplina_codigo": "CAD123",
      "disciplina_nome": "Direito Tributário",
      "instituicao_origem": "UFABC",
      "disciplina_origem_nome": "Direito Tributário",
      "certificacao_id": "certificacao_administracao_CAD123_72af1a",
      "status": "certificada",
      "data_certificacao": "2026-03-25"
    }
  ]
}
```

---

# 6. PARSER ESTRUTURAL DOS PROGRAMAS

## 6.1 Objetivo do parser

Converter texto bruto ou extraído de PDF em estrutura formal com:

* unidades;
* tópicos;
* subtópicos;
* bibliografia;
* carga horária.

## 6.2 Regras mínimas de reconhecimento

### Unidades

Reconhecer padrões como:

* `UNIDADE 1`
* `UNIDADE I`
* `MÓDULO 1`
* `UNIDADE TEMÁTICA 1`

### Tópicos

Reconhecer padrões como:

* `1.1`
* `2.3`
* `7.2`

### Subtópicos

Reconhecer padrões como:

* `4.5.1`
* `7.2.3`

### Bibliografia

Reconhecer padrões:

* `BIBLIOGRAFIA`
* `BIBLIOGRAFIA BÁSICA`
* `BIBLIOGRAFIA COMPLEMENTAR`
* `REFERÊNCIAS`

### Carga horária

Reconhecer termos:

* `Carga Horária`
* `CH`
* `horas`
* `h/a`
* `horas-aula`
* formatos como `60h`, `45 h`, `72 horas`

## 6.3 Pipeline do parser

1. ler input;
2. normalizar encoding UTF-8;
3. remover espaços duplicados;
4. padronizar quebras de linha;
5. identificar seções;
6. montar árvore hierárquica;
7. extrair carga horária;
8. extrair bibliografia;
9. salvar JSON estruturado.

## 6.4 Casos de falha

Se o parser não identificar claramente a estrutura:

* manter texto bruto salvo;
* gerar marcação `estrutura_parcial`;
* permitir revisão humana posterior.

---

# 7. MOTOR DE COMPARAÇÃO

## 7.1 Princípios

A comparação **não utiliza LLM**. Ela deve ser explicável, reproduzível e auditável.

## 7.2 Abordagem

Combinar:

* normalização textual;
* tokenização;
* remoção de stopwords em português;
* n-grams;
* TF-IDF;
* similaridade do cosseno;
* dicionário de equivalências/sinônimos;
* heurísticas de proximidade estrutural.

## 7.3 Estratégia de matching

Para cada item do programa UFSM:

1. gerar vetor textual normalizado;
2. comparar com todos os itens candidatos do programa externo;
3. calcular score composto;
4. selecionar melhor candidato;
5. classificar como equivalente, parcial ou ausente.

## 7.4 Score composto sugerido

```text
score_final =
  (0.55 * cosine_tfidf) +
  (0.20 * overlap_keywords) +
  (0.15 * ngram_similarity) +
  (0.10 * synonym_bonus)
```

Esses pesos devem ser configuráveis em arquivo de configuração do sistema.

## 7.5 Thresholds sugeridos

* `>= 0.75` = equivalente
* `>= 0.45 e < 0.75` = parcialmente equivalente
* `< 0.45` = ausente

## 7.6 Regras para carga horária

Após extração:

* se ambas existirem, calcular automaticamente;
* se faltar uma, solicitar preenchimento manual antes da conclusão;
* registrar a fonte do dado.

## 7.7 Justificativa explicável

Cada match deve armazenar:

* texto do item UFSM;
* texto do item externo associado;
* score bruto;
* score final;
* principais palavras coincidentes;
* se houve bônus por sinônimos;
* classificação final.

---

# 8. FLUXO DE REUSO E MEMÓRIA INSTITUCIONAL

## 8.1 Busca prévia antes de nova análise

Sempre que uma nova análise for solicitada, o sistema deve:

1. identificar a disciplina UFSM alvo;
2. buscar certificações já existentes para a mesma disciplina;
3. buscar análises prévias semelhantes;
4. sugerir reaproveitamento.

## 8.2 Tipos de reuso

* reuso informativo: mostrar certificadas semelhantes;
* reuso parcial: aproveitar programa externo já estruturado;
* reuso completo: duplicar análise prévia como base de nova análise.

## 8.3 Regra da homepage para alunos

Na homepage deve existir um campo de consulta com:

* curso UFSM;
* disciplina UFSM.

Ao selecionar esses campos, o sistema deve mostrar imediatamente as equivalências certificadas ativas.

---

# 9. BACKEND — ESPECIFICAÇÃO DETALHADA

## 9.1 Linguagem e framework recomendados

### Recomendação principal

* **Rust**
* **Axum** como framework web

### Justificativa

Rust oferece melhor robustez estrutural, segurança de memória e bom desempenho. Como a persistência será em arquivo local e o sistema exigirá escrita segura, concorrência controlada e validação forte, Rust é especialmente adequado.

## 9.2 Estrutura sugerida do backend

```text
/backend
  /src
    main.rs
    app.rs
    config.rs
    error.rs
    /api
      mod.rs
      auth.rs
      programs.rs
      analyses.rs
      certifications.rs
      public_search.rs
      uploads.rs
    /application
      mod.rs
      program_service.rs
      analysis_service.rs
      certification_service.rs
      public_search_service.rs
    /domain
      mod.rs
      program.rs
      analysis.rs
      certification.rs
      user.rs
      enums.rs
    /infrastructure
      mod.rs
      file_store.rs
      index_store.rs
      json_repository.rs
      lock_manager.rs
      pdf_extractor.rs
      parser.rs
      comparator.rs
      report_generator.rs
      logger.rs
    /dto
      mod.rs
      requests.rs
      responses.rs
    /utils
      mod.rs
      slug.rs
      datetime.rs
      text.rs
      validation.rs
  Cargo.toml
```

## 9.3 Camadas do backend

### Camada API

Responsável por:

* receber requests HTTP;
* validar payloads;
* autenticar usuário;
* encaminhar para serviços;
* retornar responses padronizadas.

### Camada Application

Responsável por:

* orquestrar fluxos de negócio;
* chamar parser, comparador, repositórios de arquivo e indexadores;
* aplicar regras de negócio.

### Camada Domain

Responsável por:

* modelar entidades;
* centralizar enums e invariantes.

### Camada Infrastructure

Responsável por:

* ler/escrever JSON;
* manter índices;
* extrair PDF;
* gerar relatórios;
* controlar locks de arquivo.

## 9.4 Responsabilidades centrais por serviço

### ProgramService

* cadastrar programa UFSM;
* cadastrar programa externo;
* salvar programa em JSON;
* buscar programa por id;
* listar programas por filtros.

### AnalysisService

* criar análise;
* processar parser;
* validar carga horária;
* executar comparação;
* salvar resultado;
* buscar análise;
* buscar análises reutilizáveis.

### CertificationService

* receber decisão da coordenação;
* validar status anterior;
* gerar JSON de certificação;
* atualizar índice público;
* listar certificadas por disciplina/curso.

### PublicSearchService

* buscar equivalências certificadas;
* filtrar por curso e disciplina;
* montar resposta resumida para alunos.

## 9.5 Estratégia de autenticação

MVP:

* autenticação por sessão simples ou JWT;
* perfis: `admin`, `coordenacao`, `secretaria`, `consulta`.

Consulta pública de equivalências certificadas pode ser aberta, desde que mostre somente dados permitidos.

## 9.6 Upload de arquivos

### Regras

* aceitar apenas PDF;
* validar MIME type;
* limitar tamanho máximo configurável;
* salvar o arquivo em `/data/uploads/pdf`;
* gerar nome interno único;
* registrar referência no JSON do programa.

## 9.7 Extração de PDF

### Estratégia

* primeiro tentar extração textual direta;
* se falhar, registrar falha;
* OCR apenas opcional em versão posterior.

## 9.8 Estratégia de logs

Logs em arquivos locais estruturados, por exemplo JSON Lines:

```text
/data/logs/app.log
/data/logs/error.log
/data/logs/audit.log
```

Campos mínimos:

* timestamp;
* usuário;
* endpoint;
* ação;
* resultado;
* ids afetados.

## 9.9 Tratamento de erros

Criar camada de erro com categorias:

* validation_error
* not_found
* conflict
* file_io_error
* parse_error
* comparison_error
* unauthorized
* forbidden
* internal_error

Todas as respostas de erro devem retornar payload consistente.

---

# 10. API — ENDPOINTS DETALHADOS

## 10.1 Convenção geral

Base path:

```text
/api/v1
```

## 10.2 Healthcheck

### GET /api/v1/health

Retorna status do backend.

**Response 200**

```json
{
  "status": "ok",
  "service": "curriculum-equivalence-api",
  "version": "1.0.0"
}
```

## 10.3 Upload de PDF

### POST /api/v1/uploads/pdf

Faz upload do PDF e retorna referência interna.

**Multipart form-data**

* `file`

**Response 201**

```json
{
  "upload_id": "upl_001",
  "path": "data/uploads/pdf/upl_001.pdf",
  "filename": "programa.pdf"
}
```

## 10.4 Cadastro de programa por texto

### POST /api/v1/programs/text

**Request**

```json
{
  "tipo": "externo",
  "codigo": "DIRTRIB01",
  "nome": "Direito Tributário",
  "instituicao": "UFABC",
  "curso": "Administração Pública",
  "curso_ufsm": null,
  "raw_text": "texto integral do programa",
  "carga_horaria_informada": null
}
```

**Response 201**

```json
{
  "program_id": "ext_ufabc_direito_tributario",
  "status": "created"
}
```

## 10.5 Cadastro de programa por PDF

### POST /api/v1/programs/pdf

**Request**

```json
{
  "tipo": "externo",
  "codigo": "DIRTRIB01",
  "nome": "Direito Tributário",
  "instituicao": "UFABC",
  "curso": "Administração Pública",
  "upload_id": "upl_001",
  "carga_horaria_informada": null
}
```

## 10.6 Obter programa

### GET /api/v1/programs/{program_id}

Retorna JSON completo do programa.

## 10.7 Buscar programas UFSM

### GET /api/v1/ufsm/disciplines?curso=administracao&query=tributario

Retorna lista resumida para autocomplete e filtros.

## 10.8 Criar análise

### POST /api/v1/analyses

**Request**

```json
{
  "ufsm_program_id": "ufsm_CAD123",
  "external_program_id": "ext_ufabc_direito_tributario",
  "threshold_content": 75,
  "threshold_workload": 75,
  "reprocess": true
}
```

**Response 201**

```json
{
  "analysis_id": "analise_20260325T154501Z_a82c19",
  "status": "pendente_certificacao",
  "content_score": 81.25,
  "workload_score": 75.0,
  "resultado_tecnico": "pre_aprovavel_tecnicamente"
}
```

## 10.9 Obter análise

### GET /api/v1/analyses/{analysis_id}

Retorna JSON completo da análise.

## 10.10 Listar análises reutilizáveis

### GET /api/v1/analyses/reuse?ufsm_program_id=ufsm_CAD123&external_query=ufabc

Retorna análises semelhantes para reuso.

## 10.11 Certificar análise

### POST /api/v1/certifications

**Request**

```json
{
  "analysis_id": "analise_20260325T154501Z_a82c19",
  "decisao": "deferida",
  "status": "certificada",
  "ressalvas": null,
  "publicavel_para_consulta": true
}
```

**Response 201**

```json
{
  "certification_id": "certificacao_administracao_CAD123_72af1a",
  "status": "certificada"
}
```

## 10.12 Obter certificação

### GET /api/v1/certifications/{certification_id}

## 10.13 Consulta pública de equivalências certificadas

### GET /api/v1/public/equivalences?curso=administracao&disciplina=CAD123

**Response 200**

```json
{
  "items": [
    {
      "curso": "Administração",
      "disciplina_codigo": "CAD123",
      "disciplina_nome": "Direito Tributário",
      "instituicao_origem": "UFABC",
      "disciplina_origem_nome": "Direito Tributário",
      "status": "certificada",
      "data_certificacao": "2026-03-25"
    }
  ]
}
```

## 10.14 Exportar relatório

### GET /api/v1/analyses/{analysis_id}/report.pdf

Gera e retorna PDF da análise.

---

# 11. FRONTEND — REQUISITOS DE TELA

## 11.1 Homepage

Deve conter:

* explicação resumida do sistema;
* campo de consulta rápida para alunos;
* filtros por curso UFSM e disciplina;
* lista de equivalências certificadas correspondentes;
* botão “Nova análise” para usuários autorizados.

## 11.2 Tela de nova análise

Duas colunas:

* Programa UFSM
* Programa externo

Cada coluna deve permitir:

* buscar programa já salvo;
* colar texto;
* enviar PDF;
* visualizar preview do texto extraído;
* visualizar carga horária identificada;
* informar carga horária manual se faltante.

## 11.3 Tela de resultado da análise

Deve mostrar:

* score de conteúdo;
* score de carga horária;
* status técnico;
* tabela item a item;
* alertas normativos;
* análises semelhantes já existentes;
* botão para enviar à certificação.

## 11.4 Tela de certificação

Exclusiva para coordenação, com:

* dados da análise;
* decisão;
* ressalvas;
* opção de publicação para consulta pública.

---

# 12. DIAGRAMAS

## 12.1 Arquitetura

```text
[ Navegador / Frontend Next.js ]
              |
              v
[ API REST Axum / Rust Backend ]
              |
    -----------------------------
    |             |             |
    v             v             v
[ Parser ]   [ Comparator ] [ Report Generator ]
    |             |             |
    ---------------             |
            |                   |
            v                   v
     [ JSON File Store ]   [ PDF Report Output ]
            |
            v
       [ Index Files ]
```

## 12.2 Fluxo principal

```text
Usuário inicia análise
   -> informa ou busca disciplina UFSM
   -> informa programa externo (texto/PDF)
   -> backend extrai e estrutura
   -> backend verifica carga horária
   -> se faltar, solicita input manual
   -> backend compara conteúdo
   -> backend gera análise JSON
   -> coordenação revisa
   -> coordenação certifica
   -> sistema atualiza índice público
```

## 12.3 Fluxo de consulta do aluno

```text
Aluno acessa homepage
   -> seleciona curso UFSM
   -> seleciona disciplina UFSM
   -> backend consulta index_consulta_publica.json
   -> retorna certificações ativas
   -> frontend mostra equivalências certificadas
```

---

# 13. SEGURANÇA E INTEGRIDADE

## 13.1 Segurança mínima

* validação rigorosa de input;
* sanitização de nomes de arquivos;
* rejeição de PDFs inválidos;
* autenticação para áreas restritas;
* segregação entre área pública e área administrativa.

## 13.2 Integridade dos JSON

* schema validation antes de salvar;
* escrita atômica;
* backup periódico da pasta `/data`;
* checksum opcional em fase posterior.

## 13.3 Auditoria

Toda ação crítica deve gerar log:

* criação de programa;
* geração de análise;
* reprocessamento;
* certificação;
* alteração de índice público.

---

# 14. REQUISITOS NÃO FUNCIONAIS

## 14.1 Desempenho

* busca pública em até 1 segundo para base local moderada;
* criação de análise síncrona para documentos simples;
* processamento de PDF em poucos segundos para arquivos textuais.

## 14.2 Portabilidade

O sistema deve rodar localmente em servidor Linux ou VPS simples com volume persistente.

## 14.3 Backup

Backup da pasta `/data` deve ser suficiente para recuperação funcional do sistema.

## 14.4 Observabilidade

* logs legíveis;
* mensagens de erro claras;
* healthcheck.

---

# 15. ROADMAP TÉCNICO SUGERIDO

## Fase 1 — MVP funcional

* cadastro por texto;
* upload de PDF textual;
* parser básico;
* comparação de conteúdo;
* persistência em JSON;
* certificação;
* consulta pública simples.

## Fase 2 — Robustez

* OCR opcional;
* dicionário de sinônimos administrável;
* relatórios DOCX;
* locks de arquivo mais robustos.

## Fase 3 — Escala institucional

* integração com autenticação institucional;
* importação em lote de programas UFSM;
* painel analítico;
* assinatura eletrônica institucional.

---

# 16. CRITÉRIOS DE ACEITE

O sistema será considerado pronto quando:

* permitir cadastro de programa por texto e PDF;
* gerar JSON estruturado para programas UFSM e externos;
* salvar análises em JSON;
* calcular equivalência de conteúdo e carga horária;
* solicitar carga horária manual quando não identificada;
* permitir certificação pela coordenação;
* atualizar consulta pública de certificadas;
* reaproveitar análises anteriores;
* expor endpoints documentados;
* manter backend organizado em camadas.

---

# 17. OBSERVAÇÃO FINAL AO DESENVOLVEDOR

Este sistema não deve ser tratado como simples comparador textual. Ele é um sistema institucional de apoio à decisão acadêmica, com memória local persistente, rastreabilidade normativa, fluxo formal de certificação e interface de consulta para estudantes.

O backend precisa ser desenvolvido de forma suficientemente detalhada para garantir:

* segurança de escrita em arquivos;
* consistência entre índices e documentos JSON;
* clareza de manutenção;
* possibilidade de evolução futura.
