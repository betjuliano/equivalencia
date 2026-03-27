'use client';
import { useState, useEffect } from 'react';
import { createProgramText, uploadPdf, createProgramPdf, searchUfsmDisciplines, ProgramIndexItem } from '@/lib/api';

type ProgramType = 'ufsm' | 'externo';

interface Props {
  tipo: ProgramType;
  title: string;
  onProgramCreated: (id: string, data: any) => void;
}

export default function ProgramInput({ tipo, title, onProgramCreated }: Props) {
  const [tab, setTab] = useState<'search' | 'text' | 'pdf'>(tipo === 'ufsm' ? 'text' : 'text');
  
  // States for UFSM Cursos dropdown
  const [cursosUfsm, setCursosUfsm] = useState<string[]>([]);
  const [selectedCursoUfsm, setSelectedCursoUfsm] = useState('');
  const [disciplinasUfsm, setDisciplinasUfsm] = useState<any[]>([]);
  const [isManualUfsm, setIsManualUfsm] = useState(false);

  // Form state
  const [codigo, setCodigo] = useState('');
  const [nome, setNome] = useState('');
  const [instituicao, setInst] = useState(tipo === 'ufsm' ? 'UFSM' : '');
  const [curso, setCurso] = useState('');
  const [ch, setCh] = useState('');
  const [semestre, setSemestre] = useState('');
  const [tipoDisc, setTipoDisc] = useState('OBR');
  const [nucleo, setNucleo] = useState('Formação Profissional');
  const [tppext, setTppext] = useState('0-0-0-0');
  const [rawText, setRawText] = useState('');
  const [isPermanent, setIsPermanent] = useState(false);
  const [newCursoName, setNewCursoName] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [userRole, setUserRole] = useState<string | null>(null);

  // Load Cursos UFSM and User Role on mount
  useEffect(() => {
    if (tipo === 'ufsm') {
      import('@/lib/api').then((api) => {
        api.getCursosUfsm().then(res => setCursosUfsm(res.cursos)).catch(console.error);
        const token = api.getToken();
        if (token) {
           try {
             const payload = JSON.parse(atob(token.split('.')[1]));
             setUserRole(payload.role);
           } catch(e) {}
        }
      });
    }
  }, [tipo]);

  // Load Disciplinas when Curso is selected
  useEffect(() => {
    if (tipo === 'ufsm' && selectedCursoUfsm) {
      import('@/lib/api').then((api) => {
        api.getDisciplinasCurso(selectedCursoUfsm)
          .then(res => setDisciplinasUfsm(res.disciplinas))
          .catch(console.error);
      });
    } else {
      setDisciplinasUfsm([]);
    }
  }, [selectedCursoUfsm, tipo]);

  const handleSelectDisciplina = (jsonItem: any) => {
    setCodigo(jsonItem.codigo || '');
    setNome(jsonItem.nome || '');
    setCh((jsonItem.ch_total || '').toString());
    setSemestre((jsonItem.semestre || '').toString());
    setTipoDisc(jsonItem.tipo || 'OBR');
    setNucleo(jsonItem.nucleo_grupo || 'Formação Profissional');
    setTppext(jsonItem.t_p_pext || '0-0-0-0');
    setRawText(jsonItem.programa || '');
    setCurso(selectedCursoUfsm);
    setIsManualUfsm(false);
  };

  const handleManualSelect = () => {
    setCodigo('');
    setNome('');
    setCh('');
    setCurso(selectedCursoUfsm);
    setIsManualUfsm(true);
  };

  const handleSubmitText = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const { createProgramText, createDisciplinaUfsm } = await import('@/lib/api');
      
      const finalCurso = selectedCursoUfsm === 'NEW_COURSE' ? newCursoName : (selectedCursoUfsm || curso);

      if (tipo === 'ufsm' && isPermanent) {
        if (isManualUfsm || selectedCursoUfsm === 'NEW_COURSE') {
          await createDisciplinaUfsm(finalCurso, {
            codigo, nome, semestre: semestre ? Number(semestre) : undefined,
            tipo: tipoDisc, ch_total: Number(ch), nucleo_grupo: nucleo,
            programa: rawText, t_p_pext: tppext
          });
        } else {
          const { updateDisciplinaUfsm } = await import('@/lib/api');
          await updateDisciplinaUfsm(finalCurso, codigo, {
            nome, semestre: semestre ? Number(semestre) : undefined,
            tipo: tipoDisc, ch_total: Number(ch), nucleo_grupo: nucleo,
            programa: rawText, t_p_pext: tppext
          });
        }
      }

      if (tipo === 'externo' && isPermanent) {
        const { createDisciplinaExterna } = await import('@/lib/api');
        await createDisciplinaExterna(instituicao, curso, {
           codigo, nome, instituicao, curso_origem: curso,
           ch_total: Number(ch), programa: rawText,
           semestre: semestre ? Number(semestre) : undefined
        });
      }

      const res = await createProgramText({
        tipo, codigo, nome, 
        instituicao: tipo === 'externo' ? instituicao : undefined,
        curso_ufsm: tipo === 'ufsm' ? finalCurso : undefined,
        curso: tipo === 'externo' ? (curso || finalCurso) : undefined,
        raw_text: rawText,
        carga_horaria_informada: ch ? Number(ch) : undefined,
      });
      onProgramCreated(res.program_id, { codigo, nome, curso: finalCurso || curso });
    } catch (err) { alert('Erro ao salvar'); }
    finally { setLoading(false); }
  };

  const handleSubmitPdf = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;
    setLoading(true);
    try {
      const { uploadPdf, createProgramPdf } = await import('@/lib/api');
      const up = await uploadPdf(file);
      const res = await createProgramPdf({
        tipo: 'externo', codigo, nome, instituicao, curso,
        upload_id: up.upload_id,
        carga_horaria_informada: ch ? Number(ch) : undefined,
      });
      onProgramCreated(res.program_id, { codigo, nome, curso });
    } catch (err) { alert('Erro ao processar PDF'); }
    finally { setLoading(false); }
  };

  return (
    <div className="card h-full flex flex-col">
      <h3 className="card-title text-lg">{title}</h3>
      
      <div className="tabs mb-3">
        <button className={`tab ${tab === 'text' ? 'active' : ''}`} onClick={() => setTab('text')}>Formulário</button>
        {tipo === 'externo' && (
          <button className={`tab ${tab === 'pdf' ? 'active' : ''}`} onClick={() => setTab('pdf')}>PDF</button>
        )}
      </div>

      <div className="flex-1 overflow-y-auto pr-2" style={{ maxHeight: '600px' }}>
        {tab === 'text' && (
          <form onSubmit={handleSubmitText}>
            
            {/* UFSM Dynamic Dropdowns */}
            {tipo === 'ufsm' && (
              <div className="mb-3 p-3 bg-base border border-blue-100 rounded">
                <div className="form-group">
                  <label className="form-label text-primary-dark font-semibold">1. Selecione o Curso UFSM</label>
                  <select 
                    className="form-input" 
                    value={selectedCursoUfsm} 
                    onChange={e => {
                      setSelectedCursoUfsm(e.target.value);
                      setIsManualUfsm(false);
                      setCodigo(''); setNome(''); setCh('');
                    }}
                  >
                    <option value="">-- Selecione o Curso --</option>
                    {cursosUfsm.map(c => <option key={c} value={c}>{c}</option>)}
                    <option value="NEW_COURSE" className="font-bold text-accent">+ Cadastrar Novo Curso</option>
                  </select>
                </div>

                {selectedCursoUfsm === 'NEW_COURSE' && (
                  <div className="form-group mt-2 mb-2">
                    <label className="form-label text-accent font-bold">Nome do Novo Curso</label>
                    <input 
                      type="text" 
                      className="form-input border-accent" 
                      placeholder="Ex: Sistemas de Informação"
                      value={newCursoName}
                      onChange={e => {
                        setNewCursoName(e.target.value);
                        setIsManualUfsm(true);
                      }}
                      required
                    />
                  </div>
                )}

                {(selectedCursoUfsm && selectedCursoUfsm !== 'NEW_COURSE') && (
                  <div className="form-group mt-2">
                    <label className="form-label text-primary-dark font-semibold">2. Selecione a Disciplina</label>
                    <select 
                      className="form-input" 
                      onChange={e => {
                        if (e.target.value === 'MANUAL') {
                          handleManualSelect();
                        } else if (e.target.value) {
                          const item = disciplinasUfsm.find(d => d.codigo === e.target.value);
                          if (item) handleSelectDisciplina(item);
                        }
                      }}
                      value={isManualUfsm ? 'MANUAL' : (codigo || '')}
                      required
                    >
                      <option value="">-- Busque e selecione a disciplina --</option>
                      {disciplinasUfsm.map(d => (
                        <option key={d.codigo} value={d.codigo}>
                          {d.codigo} - {d.nome} ({d.ch_total}h)
                        </option>
                      ))}
                      {userRole && (
                        <option value="MANUAL" className="font-bold text-accent">
                          + Não encontrei minha disciplina na lista (Inserção Manual)
                        </option>
                      )}
                    </select>
                  </div>
                )}
              </div>
            )}

            {/* Program Details */}
            {((tipo === 'externo') || (tipo === 'ufsm' && (codigo || isManualUfsm || selectedCursoUfsm === 'NEW_COURSE'))) && (
              <div className="card bg-gray-50 border-gray-200 mt-2 p-3">
                <div className="two-col mb-1">
                  <div>
                    <label className="form-label">Código</label>
                    <input type="text" className="form-input" required value={codigo} onChange={e=>setCodigo(e.target.value)} disabled={tipo === 'ufsm' && !isManualUfsm && selectedCursoUfsm !== 'NEW_COURSE' && !userRole} />
                  </div>
                  <div>
                    <label className="form-label">Nome</label>
                    <input type="text" className="form-input" required value={nome} onChange={e=>setNome(e.target.value)} disabled={tipo === 'ufsm' && !isManualUfsm && selectedCursoUfsm !== 'NEW_COURSE' && !userRole} />
                  </div>
                </div>

                {tipo === 'ufsm' && (isManualUfsm || selectedCursoUfsm === 'NEW_COURSE' || (userRole && !isManualUfsm)) && (
                  <div className="grid grid-cols-2 gap-2 mb-2 p-2 bg-white border rounded">
                    <div>
                      <label className="form-label text-xs">Semestre</label>
                      <input type="number" className="form-input text-sm" value={semestre} onChange={e=>setSemestre(e.target.value)} placeholder="Ex: 5" />
                    </div>
                    <div>
                      <label className="form-label text-xs">Tipo</label>
                      <select className="form-input text-sm" value={tipoDisc} onChange={e=>setTipoDisc(e.target.value)}>
                        <option value="OBR">OBR (Obrigatória)</option>
                        <option value="ELE">ELE (Eletiva)</option>
                        <option value="DCG">DCG</option>
                        <option value="DCEX">DCEX</option>
                      </select>
                    </div>
                    <div>
                      <label className="form-label text-xs">Núcleo/Grupo</label>
                      <select className="form-input text-sm" value={nucleo} onChange={e=>setNucleo(e.target.value)}>
                        <option value="Formação Básica">Formação Básica</option>
                        <option value="Formação Profissional">Formação Profissional</option>
                        <option value="Quantitativos">Quantitativos</option>
                        <option value="Complementares">Complementares</option>
                      </select>
                    </div>
                    <div>
                      <label className="form-label text-xs" title="Teórica - Prática - Prática Extensionista - EAD">
                        T-P-PEXT-EAD (?)
                      </label>
                      <input 
                        type="text" 
                        className="form-input text-sm" 
                        value={tppext} 
                        placeholder="Ex: 60-0-0-0"
                        onBlur={e => {
                          const val = e.target.value;
                          if (!val) return;
                          if (val.includes('-')) {
                            const parts = val.split('-').map(p => p.trim() || '0');
                            while (parts.length < 4) parts.push('0');
                            const formatted = parts.slice(0, 4).join('-');
                            setTppext(formatted);
                            // Auto-sum
                            const sum = parts.slice(0, 4).reduce((a, b) => a + (parseInt(b) || 0), 0);
                            setCh(sum.toString());
                          } else if (!isNaN(Number(val))) {
                            const match = val.match(/^0+/);
                            const leadingZeros = match ? match[0].length : 0;
                            const num = parseInt(val, 10) || 0;
                            const parts = ['0', '0', '0', '0'];
                            const idx = Math.min(leadingZeros, 3);
                            parts[idx] = num.toString();
                            const formatted = parts.join('-');
                            setTppext(formatted);
                            // Auto-sum
                            const sum = parts.reduce((a, b) => a + (parseInt(b) || 0), 0);
                            setCh(sum.toString());
                          }
                        }}
                        onChange={e => setTppext(e.target.value)}
                      />
                    </div>
                  </div>
                )}
                <div className="two-col mb-1">
                  {tipo === 'externo' && (
                    <div>
                      <label className="form-label">Instituição</label>
                      <input type="text" className="form-input" required value={instituicao} onChange={e=>setInst(e.target.value)} />
                    </div>
                  )}
                  {tipo === 'externo' && (
                    <div>
                      <label className="form-label">Curso de Origem</label>
                      <input type="text" className="form-input" required value={curso} onChange={e=>setCurso(e.target.value)} />
                    </div>
                  )}
                </div>
                <div className="form-group mb-2">
                  <label className="form-label">Carga Horária Total (Horas-aula)</label>
                  <input type="number" className="form-input" required value={ch} onChange={e=>setCh(e.target.value)} disabled={tipo === 'ufsm' && !isManualUfsm && selectedCursoUfsm !== 'NEW_COURSE'} />
                  {selectedCursoUfsm === 'Administracao' && tppext.includes('-') && (
                    <p className="text-[10px] text-blue-600 mt-1">
                      * Administracao (100% presencial): EAD ({tppext.split('-')[3] || 0}h) {Number(tppext.split('-')[3]) > 0 ? 'desconsiderado' : 'válido'} para análise oficial.
                    </p>
                  )}
                </div>
                {((tipo === 'externo') || (tipo === 'ufsm' && (isManualUfsm || selectedCursoUfsm === 'NEW_COURSE' || userRole))) && (
                  <div className="flex flex-col gap-2 mb-3">
                    {tipo === 'ufsm' && (isManualUfsm || selectedCursoUfsm === 'NEW_COURSE') && (
                       <p className="text-xs text-orange-600 font-semibold bg-orange-50 p-2 rounded">⚠️ Cadastro manual: As informações fornecidas estarão sujeitas a validação da coordenação.</p>
                    )}
                    
                    {(userRole === 'admin' || userRole === 'coordenacao' || tipo === 'externo') && (
                      <label className="flex items-center gap-2 p-2 bg-blue-50 border border-blue-200 rounded cursor-pointer hover:bg-blue-100">
                        <input type="checkbox" className="w-4 h-4" checked={isPermanent} onChange={e => setIsPermanent(e.target.checked)} />
                        <span className="text-sm font-bold text-primary">💾 Salvar Permanentemente na Matriz Oficial {tipo === 'externo' ? '(Fila de Análise)' : ''}</span>
                      </label>
                    )}
                  </div>
                )}
                
                <div className="form-group">
                  <label className="form-label font-bold text-primary">Texto do Programa da Disciplina (Ementa + Conteúdo)</label>
                  <p className="text-xs text-gray-500 mb-1">Copie do PPC ou do sistema Moodle e cole abaixo o texto contemplando a Ementa e o Conteúdo Programático completos.</p>
                  <textarea className="form-textarea h-32" required value={rawText} onChange={e=>setRawText(e.target.value)} placeholder="Cole aqui o texto descritivo do programa da disciplina..." />
                </div>
                
                <button type="submit" className="btn btn-primary w-full mt-2" disabled={loading}>
                  {loading ? 'Processando NLP...' : 'Salvar e Extrair Entidades NLP'}
                </button>
              </div>
            )}
          </form>
        )}

        {tab === 'pdf' && tipo === 'externo' && (
          <form onSubmit={handleSubmitPdf}>
            <div className="two-col mb-1">
              <div>
                <label className="form-label">Código</label>
                <input type="text" className="form-input" required value={codigo} onChange={e=>setCodigo(e.target.value)} />
              </div>
              <div>
                <label className="form-label">Nome</label>
                <input type="text" className="form-input" required value={nome} onChange={e=>setNome(e.target.value)} />
              </div>
            </div>
            <div className="two-col mb-1">
              <div>
                <label className="form-label">Instituição</label>
                <input type="text" className="form-input" required value={instituicao} onChange={e=>setInst(e.target.value)} />
              </div>
              <div>
                <label className="form-label">Curso</label>
                <input type="text" className="form-input" required value={curso} onChange={e=>setCurso(e.target.value)} />
              </div>
            </div>
            <div className="form-group">
              <label className="form-label">Carga Horária (opcional)</label>
              <input type="number" className="form-input" value={ch} onChange={e=>setCh(e.target.value)} />
            </div>
            
            <div className="form-group mt-3">
              <label className="form-label">Arquivo PDF do Programa (Autenticado)</label>
              <div className="drop-zone" onClick={() => document.getElementById('fileUpload')?.click()}>
                <input type="file" id="fileUpload" accept="application/pdf" className="hidden" style={{display: 'none'}}
                  onChange={e => setFile(e.target.files?.[0] || null)} />
                {file ? (
                  <p className="text-success font-bold">{file.name}</p>
                ) : (
                  <p className="text-muted">Clique para anexar arquivo PDF com Assinatura Eletrônica</p>
                )}
              </div>
            </div>

            <button type="submit" className="btn btn-primary w-full mt-3" disabled={!file || loading}>
              {loading ? 'Extraindo Dados...' : 'Enviar PDF'}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
