'use client';
import { useState, useEffect } from 'react';
import Link from 'next/link';
import { searchPublicEquivalences, PublicEquivalenceItem, createAnalysis } from '@/lib/api';
import ProgramInput from '@/components/ProgramInput';
import AnalysisResultView from '@/components/AnalysisResultView';

export default function Home() {
  const [tab, setTab] = useState<'analise' | 'consulta'>('analise');
  
  // Consulta Pública State
  const [curso, setCurso] = useState('');
  const [disciplina, setDisciplina] = useState('');
  const [items, setItems] = useState<PublicEquivalenceItem[]>([]);
  const [loadingConsulta, setLoadingConsulta] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);

  // Nova Análise State
  const [ufsmId, setUfsmId] = useState<string | null>(null);
  const [extIds, setExtIds] = useState<string[]>([]);
  const [loadingAnalise, setLoadingAnalise] = useState(false);
  const [analysisIdResult, setAnalysisIdResult] = useState<string | null>(null);

  useEffect(() => {
    // Initial fetch for Consultation
    handleSearchConsulta();
  }, []);

  const handleSearchConsulta = async (e?: React.FormEvent) => {
    e?.preventDefault();
    setLoadingConsulta(true);
    try {
      const res = await searchPublicEquivalences(curso, disciplina);
      setItems(res.items || []);
      setHasSearched(true);
    } catch (err) { setItems([]); } 
    finally { setLoadingConsulta(false); }
  };

  const handleCreateAnalysis = async () => {
    if (!ufsmId || extIds.length === 0) return;
    setLoadingAnalise(true);
    try {
      const res = await createAnalysis({ ufsm_program_id: ufsmId, external_program_ids: extIds });
      setAnalysisIdResult(res.analysis_id);
    } catch (err: any) { alert(err.message || 'Erro ao comparar programas'); }
    finally { setLoadingAnalise(false); }
  };

  const startNewAnalysis = () => {
    setUfsmId(null); setExtIds([]); setAnalysisIdResult(null);
  };

  return (
    <>
      <section className="hero fade-in">
        <div className="hero-content">
          <h1>Equivalência de Disciplinas <br /><span style={{ color: '#93c5fd' }}>Ágil e Acadêmica</span></h1>
          <p>Envie os programas e valide a compatibilidade de currículos 📖</p>
        </div>
      </section>

      <div className="container mt-4 mb-4" style={{ display: 'flex', gap: '1rem', justifyContent: 'center' }}>
         <button className={`btn w-full ${tab === 'analise' ? 'btn-primary' : 'btn-outline'}`} onClick={() => setTab('analise')}>
           Realizar Nova Análise (Alunos)
         </button>
         <button className={`btn w-full ${tab === 'consulta' ? 'btn-primary' : 'btn-outline'}`} onClick={() => setTab('consulta')}>
           Consultar Equivalências Aprovadas
         </button>
      </div>

      <section className="page-content container fade-in" style={{ paddingTop: 0 }}>
        {tab === 'consulta' && (
          <div className="fade-in">
            <div className="search-widget mb-4">
              <h2 className="card-title text-xl mb-3">🔍 Consulta Pública Oficial</h2>
              <form onSubmit={handleSearchConsulta} className="three-col items-center">
                <div>
                  <label className="form-label">Curso UFSM</label>
                  <input type="text" className="form-input" placeholder="Ex: Administração"
                         value={curso} onChange={e => setCurso(e.target.value)} />
                </div>
                <div>
                  <label className="form-label">Disciplina UFSM</label>
                  <input type="text" className="form-input" placeholder="Código ou Nome"
                         value={disciplina} onChange={e => setDisciplina(e.target.value)} />
                </div>
                <div style={{ paddingTop: '1.5rem' }}>
                  <button type="submit" className="btn btn-primary w-full" disabled={loadingConsulta}>
                    {loadingConsulta ? 'Buscando...' : 'Buscar Equivalências'}
                  </button>
                </div>
              </form>
            </div>

            {loadingConsulta ? (
              <div className="loading-overlay"><div className="spinner"></div><p className="text-muted">Buscando na base institucional...</p></div>
            ) : items.length > 0 ? (
              <div className="card fade-in">
                <h3 className="card-title mb-2">Resultados Certificados ({items.length})</h3>
                <div className="table-wrapper">
                  <table>
                    <thead>
                      <tr>
                        <th>Curso UFSM</th><th>Disciplina UFSM</th><th>Instituição Origem</th><th>Disciplina Origem</th><th>Data da Certificação</th>
                      </tr>
                    </thead>
                    <tbody>
                      {items.map(it => (
                        <tr key={it.certificacao_id}>
                          <td>{it.curso}</td>
                          <td><strong>{it.disciplina_codigo}</strong><br/><span className="text-muted text-sm">{it.disciplina_nome}</span></td>
                          <td>{it.instituicao_origem}</td>
                          <td>{it.disciplina_origem_nome}</td>
                          <td>
                             {new Date(it.data_certificacao).toLocaleDateString('pt-BR')}
                             <span className="badge badge-success ml-2">Deferida</span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            ) : hasSearched && (
              <div className="alert alert-info justify-center flex-col gap-2">
                <p>Nenhuma equivalência certificada encontrada.</p>
                <button className="btn btn-outline btn-sm border-blue-400 text-primary" onClick={() => setTab('analise')}>
                   Acesse: Realizar Nova Análise
                </button>
              </div>
            )}
          </div>
        )}

        {tab === 'analise' && (
          <div className="fade-in">
            {!analysisIdResult ? (
              <>
                 <div className="flex items-center justify-between mb-3">
                   <h2 className="text-xl font-bold">Solicitar Análise Técnica</h2>
                   {ufsmId && extIds.length > 0 && (
                     <button className="btn btn-success fade-in" onClick={handleCreateAnalysis} disabled={loadingAnalise}>
                       {loadingAnalise ? 'Gerando Relatório...' : '➔ Iniciar Comparação Acadêmica'}
                     </button>
                   )}
                 </div>

                 <div className="alert alert-info mb-3">
                   <strong>Instruções ao Aluno:</strong> Preencha os dados da disciplina que você deseja dispensar na UFSM (Destino) e envie o plano de ensino da disciplina que você já cursou na Instituição de Origem. O sistema gerará um índice provisório e permitirá que a coordenação certifique o pedido.
                 </div>

                 <div className="two-col" style={{ minHeight: '500px' }}>
                   <div className="flex-col gap-2">
                     {!ufsmId ? (
                       <ProgramInput tipo="ufsm" title="📚 Disciplina Ofertada pela UFSM" onProgramCreated={(id) => setUfsmId(id)} />
                     ) : (
                       <div className="card h-full flex flex-col items-center justify-center fade-in text-center p-4">
                         <div className="score-ring mb-2" style={{ width: '80px', height: '80px' }}><span className="text-4xl">✅</span></div>
                         <h3 className="font-bold">Disciplina UFSM Selecionada</h3>
                         <p className="text-sm text-dim mt-1">{ufsmId}</p>
                         <button className="btn btn-outline btn-sm mt-3" onClick={() => setUfsmId(null)}>Trocar UFSM</button>
                       </div>
                     )}
                   </div>

                   <div className="flex-col gap-2">
                     <div className="flex flex-col gap-2 mb-2">
                       {extIds.map((id, index) => (
                         <div key={id} className="card flex flex-col items-center justify-center fade-in text-center p-3 border-success bg-green-50">
                           <div className="flex items-center gap-2">
                             <span className="text-xl">✅</span>
                             <h3 className="font-bold text-success">Disciplina Origem {index + 1} Inserida</h3>
                           </div>
                           <p className="text-xs text-dim mt-1">{id}</p>
                           <button className="btn btn-outline btn-sm mt-2 text-danger hover:bg-danger hover:text-white" onClick={() => setExtIds(extIds.filter(e => e !== id))}>Remover Esta</button>
                         </div>
                       ))}
                     </div>
                     <ProgramInput key={`ext-${extIds.length}`} tipo="externo" title={extIds.length > 0 ? "➕ Adicionar Outra Disciplina de Origem" : "📄 Disciplina de Origem (Aproveitamento)"} onProgramCreated={(id) => setExtIds([...extIds, id])} />
                   </div>
                 </div>
              </>
            ) : (
              <div className="fade-in">
                 <div className="flex justify-between items-center bg-bg-card p-4 rounded-lg border border-border mt-2 mb-2">
                    <div>
                        <h3 className="font-bold text-success text-xl mb-1">✓ Análise Registrada com Sucesso</h3>
                        <p className="text-muted">A Coordenação foi notificada. Você pode visualizar o parecer preliminar do algoritmo abaixo.</p>
                    </div>
                    <button className="btn btn-primary" onClick={startNewAnalysis}>Voltar e Fazer Nova</button>
                 </div>
                 <AnalysisResultView analysisId={analysisIdResult} />
              </div>
            )}
          </div>
        )}
      </section>
    </>
  );
}
