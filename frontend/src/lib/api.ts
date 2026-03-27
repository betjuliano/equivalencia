/**
 * API client for the Curriculum Equivalence Analyzer backend
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3008/api/v1';

let authToken: string | null = null;

export function setToken(token: string) {
  authToken = token;
  if (typeof window !== 'undefined') localStorage.setItem('cea_token', token);
}

export function getToken(): string | null {
  if (authToken) return authToken;
  if (typeof window !== 'undefined') {
    authToken = localStorage.getItem('cea_token');
    return authToken;
  }
  return null;
}

export function clearToken() {
  authToken = null;
  if (typeof window !== 'undefined') localStorage.removeItem('cea_token');
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> || {}),
  };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

// ── Auth ────────────────────────────────────────────────────────────────────
export async function login(username: string, password: string) {
  const form = new URLSearchParams({ username, password });
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST', body: form,
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  });
  if (!res.ok) throw new Error('Usuário ou senha incorretos');
  const data = await res.json();
  setToken(data.access_token);
  return data;
}

// ── Health ───────────────────────────────────────────────────────────────────
export const health = () => request<{ status: string }>('/health');

// ── Public ───────────────────────────────────────────────────────────────────
export const searchPublicEquivalences = (curso?: string, disciplina?: string) => {
  const q = new URLSearchParams();
  if (curso) q.append('curso', curso);
  if (disciplina) q.append('disciplina', disciplina);
  return request<{ items: PublicEquivalenceItem[] }>(`/public/equivalences?${q}`);
};

// ── Programs ─────────────────────────────────────────────────────────────────
export const searchUfsmDisciplines = (curso?: string, query?: string) => {
  const q = new URLSearchParams();
  if (curso) q.append('curso', curso);
  if (query) q.append('query', query);
  return request<ProgramIndexItem[]>(`/ufsm/disciplines?${q}`);
};

export const getCursosUfsm = () => request<{cursos: string[]}>('/cursos');
export const getDisciplinasCurso = (curso: string) => request<{curso: string, total: number, disciplinas: any[]}>(`/cursos/${encodeURIComponent(curso)}/disciplinas`);
export const createDisciplinaUfsm = (curso: string, body: any) => 
  request<any>(`/cursos/${encodeURIComponent(curso)}/disciplinas`, {
    method: 'POST', body: JSON.stringify(body)
  });
export const updateDisciplinaUfsm = (curso: string, codigo: string, body: any) => 
  request<any>(`/cursos/${encodeURIComponent(curso)}/disciplinas/${encodeURIComponent(codigo)}`, {
    method: 'PATCH', body: JSON.stringify(body)
  });
export const createDisciplinaExterna = (inst: string, curso: string, body: any) => 
  request<any>(`/externos/${encodeURIComponent(inst)}/${encodeURIComponent(curso)}/disciplinas`, {
    method: 'POST', body: JSON.stringify(body)
  });

export const getProgram = (id: string) => request<any>(`/programs/${id}`);

export const createProgramText = (body: CreateProgramTextRequest) =>
  request<{ program_id: string; status: string }>('/programs/text', {
    method: 'POST', body: JSON.stringify(body),
  });

export const uploadPdf = async (file: File): Promise<UploadResponse> => {
  const token = getToken();
  const form = new FormData();
  form.append('file', file);
  const res = await fetch(`${API_BASE}/uploads/pdf`, {
    method: 'POST',
    headers: token ? { Authorization: `Bearer ${token}` } : {},
    body: form,
  });
  if (!res.ok) throw new Error('Erro ao fazer upload do PDF');
  return res.json();
};

export const createProgramPdf = (body: CreateProgramPdfRequest) =>
  request<{ program_id: string; status: string }>('/programs/pdf', {
    method: 'POST', body: JSON.stringify(body),
  });

// ── Analyses ─────────────────────────────────────────────────────────────────
export const createAnalysis = (body: CreateAnalysisRequest) =>
  request<AnalysisSummary>('/analyses', { method: 'POST', body: JSON.stringify(body) });

export const getAnalysis = (id: string) => request<any>(`/analyses/${id}`);

export const searchReusable = (ufsm_program_id: string) =>
  request<any[]>(`/analyses/reuse?ufsm_program_id=${ufsm_program_id}`);

export const updateWorkload = (id: string, body: UpdateWorkloadRequest) =>
  request<any>(`/analyses/${id}/workload`, { method: 'PATCH', body: JSON.stringify(body) });

// ── Certifications ────────────────────────────────────────────────────────────
export const certify = (body: CertifyRequest) =>
  request<{ certification_id: string; status: string }>('/certifications', {
    method: 'POST', body: JSON.stringify(body),
  });

export const getCertification = (id: string) => request<any>(`/certifications/${id}`);

// ── Types ─────────────────────────────────────────────────────────────────────
export interface PublicEquivalenceItem {
  curso: string; curso_slug: string;
  disciplina_codigo: string; disciplina_nome: string;
  instituicao_origem: string; disciplina_origem_nome: string;
  certificacao_id: string; status: string; data_certificacao: string;
}

export interface ProgramIndexItem {
  id: string; codigo: string; nome: string; slug: string;
  curso: string; curso_slug: string; carga_horaria?: number;
}

export interface CreateProgramTextRequest {
  tipo: 'ufsm' | 'externo'; codigo: string; nome: string;
  instituicao?: string; curso?: string; curso_ufsm?: string;
  raw_text: string; carga_horaria_informada?: number;
  nota?: number; aprovado?: boolean;
  modalidade?: string; possui_extensao?: boolean; e_estagio?: boolean; e_tcc?: boolean;
  versao_ppc?: string;
}

export interface CreateProgramPdfRequest {
  tipo: 'externo'; codigo: string; nome: string;
  instituicao?: string; curso?: string; upload_id: string;
  carga_horaria_informada?: number; nota?: number; aprovado?: boolean;
}

export interface UploadResponse { upload_id: string; path: string; filename: string; }

export interface CreateAnalysisRequest {
  ufsm_program_id: string; external_program_id?: string;
  external_program_ids?: string[];
  threshold_content?: number; threshold_workload?: number; reprocess?: boolean;
}

export interface AnalysisSummary {
  analysis_id: string; status: string;
  content_score: number; workload_score: number; resultado_tecnico: string;
}

export interface UpdateWorkloadRequest {
  ufsm_carga_horaria?: number; externo_carga_horaria?: number;
}

export interface CertifyRequest {
  analysis_id: string; decisao: string; status?: string;
  ressalvas?: string; publicavel_para_consulta?: boolean;
  curso?: string; disciplina_ufsm_nome?: string;
  instituicao_origem?: string; disciplina_origem_nome?: string;
}
