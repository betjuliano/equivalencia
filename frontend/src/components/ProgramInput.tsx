'use client';
import { useState, useEffect } from 'react';
import { 
  createProgramText, uploadPdf, createProgramPdf, getPdfMetadata, 
  searchUfsmDisciplines, getCursosUfsm, getDisciplinasCurso, 
  createDisciplinaUfsm, updateDisciplinaUfsm, createDisciplinaExterna,
  getInstituicoesExternas, getCursosExternos, getDisciplinasExterno,
  getToken, decodeToken, ProgramIndexItem 
} from '@/lib/api';

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

  // States for Externos dropdown
  const [instsExternas, setInstsExternas] = useState<string[]>([]);
  const [selectedInstExterna, setSelectedInstExterna] = useState('');
  const [newInstName, setNewInstName] = useState('');

  const [cursosExternos, setCursosExternos] = useState<string[]>([]);
  const [selectedCursoExterno, setSelectedCursoExterno] = useState('');
  
  const [disciplinasExternas, setDisciplinasExternas] = useState<any[]>([]);
  const [isManualExterno, setIsManualExterno] = useState(false);

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
  const [ementaText, setEmentaText] = useState(''); // text for pdf fallback
  const [isPermanent, setIsPermanent] = useState(false);
  const [newCursoName, setNewCursoName] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [lastUploadId, setLastUploadId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [userRole, setUserRole] = useState<string | null>(null);

  // Load Initial Data AND User Role on mount
  useEffect(() => {
    const token = getToken();
    const payload = decodeToken(token);
    if (payload) {
      setUserRole(payload.role);
    }

    if (tipo === 'ufsm') {
      getCursosUfsm().then(res => setCursosUfsm(res.cursos)).catch(console.error);
    } else if (tipo === 'externo') {
      getInstituicoesExternas().then(res => setInstsExternas(res.instituicoes)).catch(console.error);
    }
  }, [tipo]);

  // Load Disciplinas UFSM when Curso is selected
  useEffect(() => {
    if (tipo === 'ufsm' && selectedCursoUfsm && selectedCursoUfsm !== 'NEW_COURSE') {
      getDisciplinasCurso(selectedCursoUfsm)
        .then(res => setDisciplinasUfsm(res.disciplinas))
        .catch(console.error);
    } else if (tipo === 'ufsm') {
      setDisciplinasUfsm([]);
    }
  }, [selectedCursoUfsm, tipo]);

  // Load Cursos Externos when Inst is selected
  useEffect(() => {
    if (tipo === 'externo' && selectedInstExterna && selectedInstExterna !== 'NEW_INST') {
      getCursosExternos(selectedInstExterna)
        .then(res => setCursosExternos(res.cursos))
        .catch(console.error);
    } else if (tipo === 'externo') {
      setCursosExternos([]);
    }
  }, [selectedInstExterna, tipo]);

  // Load Disciplinas Externas when Curso is selected
  useEffect(() => {
    if (tipo === 'externo' && selectedInstExterna && selectedInstExterna !== 'NEW_INST' && selectedCursoExterno && selectedCursoExterno !== 'NEW_COURSE') {
      getDisciplinasExterno(selectedInstExterna, selectedCursoExterno)
        .then(res => setDisciplinasExternas(res.disciplinas))
        .catch(console.error);
    } else if (tipo === 'externo') {
      setDisciplinasExternas([]);
    }
  }, [selectedInstExterna, selectedCursoExterno, tipo]);

  const handleSelectDisciplinaUfsm = (jsonItem: any) => {
    setCodigo(jsonItem.codigo || '');
    setNome(jsonItem.nome || '');
    // Support both ch_total (xlsx-imported) and carga_horaria (PDF/admin-imported) field names
    const chValue = jsonItem.ch_total ?? jsonItem.carga_horaria ?? '';
    setCh(chValue.toString());
    setSemestre((jsonItem.semestre || '').toString());
    setTipoDisc(jsonItem.tipo || 'OBR');
    setNucleo(jsonItem.nucleo_grupo || 'Formação Profissional');
    setTppext(jsonItem.t_p_pext || '0-0-0-0');
    // Support both programa (xlsx) and programa_original (PDF/admin) field names
    setRawText(jsonItem.programa || jsonItem.programa_original || '');
    setCurso(selectedCursoUfsm);
    setIsManualUfsm(false);
  };

  const handleSelectDisciplinaExterna = (jsonItem: any) => {
    setCodigo(jsonItem.codigo || '');
    setNome(jsonItem.nome || '');
    setCh((jsonItem.ch_total || jsonItem.carga_horaria || '').toString());
    setSemestre((jsonItem.semestre || '').toString());
    setRawText(jsonItem.programa || jsonItem.programa_original || '');
    setInst(selectedInstExterna);
    setCurso(selectedCursoExterno);
    setIsManualExterno(false);
  };

  const handleManualSelectUfsm = () => {
    setCodigo(''); setNome(''); setCh(''); setCurso(selectedCursoUfsm);
    setIsManualUfsm(true);
  };

  const handleManualSelectExterna = () => {
    setCodigo(''); setNome(''); setCh(''); 
    setInst(selectedInstExterna); setCurso(selectedCursoExterno);
    setIsManualExterno(true);
  };

  const handleSubmitText = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const finalCursoUfsm = selectedCursoUfsm === 'NEW_COURSE' ? newCursoName : (selectedCursoUfsm || curso);
      
      const finalInstExt = selectedInstExterna === 'NEW_INST' ? newInstName : (selectedInstExterna || instituicao);
      const finalCursoExt = selectedCursoExterno === 'NEW_COURSE' ? newCursoName : (selectedCursoExterno || curso);

      if (tipo === 'ufsm' && isPermanent) {
        if (isManualUfsm || selectedCursoUfsm === 'NEW_COURSE') {
          await createDisciplinaUfsm(finalCursoUfsm, {
            codigo, nome, semestre: semestre ? Number(semestre) : undefined,
            tipo: tipoDisc, ch_total: Number(ch), nucleo_grupo: nucleo,
            programa: rawText, t_p_pext: tppext
          });
        } else {
          await updateDisciplinaUfsm(finalCursoUfsm, codigo, {
            nome, semestre: semestre ? Number(semestre) : undefined,
            tipo: tipoDisc, ch_total: Number(ch), nucleo_grupo: nucleo,
            programa: rawText, t_p_pext: tppext
          });
        }
      }

      if (tipo === 'externo' && isPermanent) {
        await createDisciplinaExterna(finalInstExt, finalCursoExt, {
           codigo, nome, instituicao: finalInstExt, curso_origem: finalCursoExt,
           ch_total: Number(ch), programa: rawText,
           semestre: semestre ? Number(semestre) : undefined
        });
      }

      let res;
      if (lastUploadId) {
        res = await createProgramPdf({
          tipo, codigo, nome, 
          instituicao: tipo === 'externo' ? finalInstExt : 'UFSM',
          curso: tipo === 'externo' ? finalCursoExt : finalCursoUfsm,
          upload_id: lastUploadId,
          carga_horaria_informada: ch ? Number(ch) : undefined,
          ementa_texto: ementaText ? ementaText : undefined,
        });
      } else {
        res = await createProgramText({
          tipo, codigo, nome, 
          instituicao: tipo === 'externo' ? finalInstExt : undefined,
          curso_ufsm: tipo === 'ufsm' ? finalCursoUfsm : undefined,
          curso: tipo === 'externo' ? finalCursoExt : undefined,
          raw_text: rawText,
          carga_horaria_informada: ch ? Number(ch) : undefined,
        });
      }
      onProgramCreated(res.program_id, { 
        codigo, 
        nome, 
        curso: tipo === 'ufsm' ? finalCursoUfsm : finalCursoExt 
      });
    } catch (err) { alert('Erro ao salvar'); }
    finally { setLoading(false); }
  };

  const handleSubmitPdf = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;
    setLoading(true);
    try {
      const up = await uploadPdf(file);
      setLastUploadId(up.upload_id);
      const meta = await getPdfMetadata(up.upload_id);
      
      if (meta.codigo) setCodigo(meta.codigo);
      if (meta.nome) setNome(meta.nome);
      if (meta.ch) setCh(meta.ch.toString());
      if (meta.instituicao && tipo === 'externo') setInst(meta.instituicao);
      if (meta.text) setRawText(meta.text);

      setTab('text'); // Switch to form tab for review
      
      // If we are in externo and PDF gave us an institution, we could try to set it but it's simpler to let user map it or use manual
      if (tipo === 'externo' && meta.instituicao) {
        setIsManualExterno(true);
      }
    } catch (err) { 
      alert('Erro ao extrair dados do PDF'); 
    } finally { 
      setLoading(false); 
    }
  };

  // Determine if form details should be displayed
  const shouldShowUfsmDetails = tipo === 'ufsm' && (codigo || isManualUfsm || selectedCursoUfsm === 'NEW_COURSE');
  const shouldShowExtDetails = tipo === 'externo' && (codigo || isManualExterno || selectedCursoExterno === 'NEW_COURSE' || selectedInstExterna === 'NEW_INST');
  const showDetails = shouldShowUfsmDetails || shouldShowExtDetails;

  return (
    <div className="card h-full flex flex-col">
      <h3 className="card-title text-lg">{title}</h3>
      
      <div className="tabs mb-3">
        <button className={`tab ${tab === 'text' ? 'active' : ''}`} onClick={() => setTab('text')}>Formulário</button>
        <button className={`tab ${tab === 'pdf' ? 'active' : ''}`} onClick={() => setTab('pdf')}>PDF</button>
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
                      setCodigo(''); setNome(''); setCh(''); setRawText('');
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
                          handleManualSelectUfsm();
                        } else if (e.target.value) {
                          const item = disciplinasUfsm.find(d => d.codigo === e.target.value);
                          if (item) handleSelectDisciplinaUfsm(item);
                        }
                      }}
                      value={isManualUfsm ? 'MANUAL' : (codigo || '')}
                      required
                    >
                      <option value="">-- Busque e selecione a disciplina --</option>
                      {disciplinasUfsm.map(d => (
                        <option key={d.codigo} value={d.codigo}>
                          {d.codigo} - {d.nome} ({d.ch_total || d.carga_horaria}h)
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

            {/* EXTERNOS Dynamic Dropdowns */}
            {tipo === 'externo' && (
              <div className="mb-3 p-3 bg-base border border-blue-100 rounded">
                <div className="form-group">
                  <label className="form-label text-primary-dark font-semibold">1. Selecione a Instituição Externa</label>
                  <select 
                    className="form-input" 
                    value={selectedInstExterna} 
                    onChange={e => {
                      setSelectedInstExterna(e.target.value);
                      setSelectedCursoExterno('');
                      setIsManualExterno(false);
                      setCodigo(''); setNome(''); setCh(''); setRawText('');
                    }}
                  >
                    <option value="">-- Selecione a Instituição --</option>
                    {instsExternas.map(i => <option key={i} value={i}>{i}</option>)}
                    <option value="NEW_INST" className="font-bold text-accent">+ Cadastrar Nova Instituição</option>
                  </select>
                </div>

                {selectedInstExterna === 'NEW_INST' && (
                  <div className="form-group mt-2 mb-2">
                    <label className="form-label text-accent font-bold">Nome da Nova Instituição</label>
                    <input 
                      type="text" 
                      className="form-input border-accent" 
                      placeholder="Ex: USP"
                      value={newInstName}
                      onChange={e => {
                        setNewInstName(e.target.value);
                        setInst(e.target.value);
                        setIsManualExterno(true);
                      }}
                      required
                    />
                  </div>
                )}

                {(selectedInstExterna && selectedInstExterna !== 'NEW_INST') && (
                  <div className="form-group mt-2">
                    <label className="form-label text-primary-dark font-semibold">2. Selecione o Curso</label>
                    <select 
                      className="form-input" 
                      value={selectedCursoExterno} 
                      onChange={e => {
                        setSelectedCursoExterno(e.target.value);
                        setIsManualExterno(false);
                        setCodigo(''); setNome(''); setCh(''); setRawText('');
                      }}
                    >
                      <option value="">-- Selecione o Curso --</option>
                      {cursosExternos.map(c => <option key={c} value={c}>{c}</option>)}
                      <option value="NEW_COURSE" className="font-bold text-accent">+ Cadastrar Novo Curso</option>
                    </select>
                  </div>
                )}

                {selectedCursoExterno === 'NEW_COURSE' && (
                  <div className="form-group mt-2 mb-2">
                    <label className="form-label text-accent font-bold">Nome do Novo Curso Externo</label>
                    <input 
                      type="text" 
                      className="form-input border-accent" 
                      placeholder="Ex: Ciência da Computação"
                      value={newCursoName}
                      onChange={e => {
                        setNewCursoName(e.target.value);
                        setCurso(e.target.value);
                        setIsManualExterno(true);
                      }}
                      required
                    />
                  </div>
                )}

                {(selectedInstExterna && selectedInstExterna !== 'NEW_INST' && selectedCursoExterno && selectedCursoExterno !== 'NEW_COURSE') && (
                  <div className="form-group mt-2">
                    <label className="form-label text-primary-dark font-semibold">3. Selecione a Disciplina</label>
                    <select 
                      className="form-input" 
                      onChange={e => {
                        if (e.target.value === 'MANUAL') {
                          handleManualSelectExterna();
                        } else if (e.target.value) {
                          const item = disciplinasExternas.find(d => d.codigo === e.target.value);
                          if (item) handleSelectDisciplinaExterna(item);
                        }
                      }}
                      value={isManualExterno ? 'MANUAL' : (codigo || '')}
                      required
                    >
                      <option value="">-- Busque e selecione a disciplina --</option>
                      {disciplinasExternas.map(d => (
                        <option key={d.codigo} value={d.codigo}>
                          {d.codigo} - {d.nome} ({d.ch_total || d.carga_horaria}h)
                        </option>
                      ))}
                      <option value="MANUAL" className="font-bold text-accent">
                        + Não encontrei minha disciplina na lista (Inserção Manual)
                      </option>
                    </select>
                  </div>
                )}
              </div>
            )}

            {/* Program Details */}
            {showDetails && (
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
                  {tipo === 'externo' && isManualExterno && selectedInstExterna === 'NEW_INST' && (
                    <div>
                      <label className="form-label text-gray-400">Instituição</label>
                      <input type="text" className="form-input bg-gray-100 text-gray-500" disabled value={newInstName} />
                    </div>
                  )}
                  {tipo === 'externo' && isManualExterno && selectedCursoExterno === 'NEW_COURSE' && (
                    <div>
                      <label className="form-label text-gray-400">Curso de Origem</label>
                      <input type="text" className="form-input bg-gray-100 text-gray-500" disabled value={newCursoName} />
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

        {tab === 'pdf' && (
          <form onSubmit={handleSubmitPdf} className="p-4 bg-white rounded shadow-sm border border-premium-gold/20">
            <h3 className="text-lg font-medium mb-4 text-premium-gold uppercase tracking-wider">Carregar via PDF</h3>
            <p className="text-sm text-gray-500 mb-4">Anexe o PDF do programa para extrair os dados automaticamente (Código, Nome, CH, etc).</p>
            <div className="mb-4">
              <input type="file" accept=".pdf" onChange={(e) => setFile(e.target.files?.[0] || null)} className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-premium-gold/10 file:text-premium-gold hover:file:bg-premium-gold/20" />
            </div>
            
            <div className="mb-4">
              <label className="form-label text-sm font-semibold text-gray-700">Texto Alternativo da Ementa (Opcional)</label>
              <p className="text-xs text-gray-400 mb-2">Caso a disciplina seja de outra instituição e o PDF falhe em ler o conteúdo de ementa (Unidades/Programa), cole o texto estruturado abaixo.</p>
              <textarea 
                className="form-textarea h-24" 
                placeholder="Exemplo: Unidade 1 - Introdução... 1.1 Conceitos..."
                value={ementaText}
                onChange={e => setEmentaText(e.target.value)}
              />
            </div>
            
            <button type="submit" disabled={loading || !file} className="btn btn-primary w-full py-3">
              {loading ? 'Extraindo...' : 'Carregar Dados do PDF'}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
