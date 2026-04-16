'use client';
import { useEffect, useState, useCallback } from 'react';
import Link from 'next/link';
import { getAnalysis, updateWorkload, searchReusable, getToken } from '@/lib/api';

export default function AnalysisResultView({ analysisId }: { analysisId: string }) {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [updateError, setUpdateError] = useState<string | null>(null);
  const [ufsmCh, setUfsmCh] = useState('');
  const [extCh, setExtCh] = useState('');
  const [reusable, setReusable] = useState<any[]>([]);
  const isCoord = !!getToken();

  const loadData = useCallback(async (signal?: AbortSignal) => {
    setLoadError(null);
    try {
      const res = await getAnalysis(analysisId);
      if (signal?.aborted) return;
      setData(res);

      // searchReusable is optional — don't let it block the result view
      try {
        if (res.ufsm_program_id) {
          const reus = await searchReusable(res.ufsm_program_id);
          if (!signal?.aborted && Array.isArray(reus)) {
            setReusable(reus.filter((r: any) => r.id !== res.id));
          }
        }
      } catch {
        // Silently ignore — reusable history is informational only
      }
    } catch (err: any) {
      if (!signal?.aborted) setLoadError(err.message || 'Erro ao carregar análise.');
    } finally {
      if (!signal?.aborted) setLoading(false);
    }
  }, [analysisId]);

  useEffect(() => {
    const controller = new AbortController();
    loadData(controller.signal);
    return () => controller.abort();
  }, [loadData]);

  const handleUpdateCH = async () => {
    if (!isCoord) { setUpdateError('Apenas a coordenação pode alterar a CH manual.'); return; }
    setUpdateError(null);
    try {
      await updateWorkload(analysisId, {
        ufsm_carga_horaria: ufsmCh ? Number(ufsmCh) : undefined,
        externo_carga_horaria: extCh ? Number(extCh) : undefined,
      });
      loadData();
    } catch (err: any) { setUpdateError(err.message || 'Erro ao atualizar CH'); }
  };

  if (loading) return <div className="loading-overlay"><div className="spinner"></div><p>Analisando currículos...</p></div>;
  if (loadError) return <div className="alert alert-error">{loadError} <button className="btn btn-outline btn-sm ml-2" onClick={() => { setLoading(true); loadData(); }}>Tentar novamente</button></div>;
  if (!data) return <div className="alert alert-error">Análise não encontrada.</div>;

  const cScore = data.content_score || 0;
  const wScore = data.workload_score || 0;

  return (
    <div className="fade-in mt-4 border-t border-border pt-4">
      {updateError && <div className="alert alert-error mb-3">{updateError}</div>}
      <div className="flex justify-between items-center mb-4">
        <div>
          <h2 className="text-xl font-bold mb-1">Resultado da Análise Preliminar</h2>
          <p className="text-muted text-sm border border-border p-1 rounded inline-block bg-bg-card">{data.id}</p>
        </div>
        <div>
          {isCoord ? (
            <Link href={`/certifications/${data.id}?create=true`} className="btn btn-success" 
                  style={{ pointerEvents: data.resultado_final === 'pendente_dados' ? 'none' : 'auto', opacity: data.resultado_final === 'pendente_dados' ? 0.5 : 1 }}>
              Enviar para Certificação
            </Link>
          ) : (
             <span className="badge badge-info">Acompanhe pelo ID</span>
          )}
        </div>
      </div>

      <div className="two-col mb-4">
        <div className="card text-center flex-col justify-center items-center">
          <h3 className="card-title justify-center">Equivalência de Conteúdo</h3>
          <div className="score-ring mt-2 mb-2">
            <svg viewBox="0 0 100 100" width="120" height="120">
              <circle cx="50" cy="50" r="45" fill="none" stroke="var(--border)" strokeWidth="8" />
              <circle cx="50" cy="50" r="45" fill="none" stroke={cScore >= 75 ? "var(--success)" : "var(--danger)"} 
                      strokeWidth="8" strokeDasharray={`${cScore * 2.83} 283`} strokeLinecap="round" />
            </svg>
            <div className="score-text">{cScore.toFixed(1)}%<br/><span className="score-label">Score</span></div>
          </div>
          <span className={`badge ${cScore >= 75 ? 'badge-success' : 'badge-danger'}`}>
            {cScore >= 75 ? 'Atende' : 'Não Atende'}
          </span>
        </div>

        <div className="card text-center flex-col justify-center items-center">
          <h3 className="card-title justify-center">Equivalência de Carga Horária</h3>
          {wScore ? (
            <>
              <div className="score-ring mt-2 mb-2">
                <svg viewBox="0 0 100 100" width="120" height="120">
                  <circle cx="50" cy="50" r="45" fill="none" stroke="var(--border)" strokeWidth="8" />
                  <circle cx="50" cy="50" r="45" fill="none" stroke={wScore >= 75 ? "var(--success)" : "var(--danger)"} 
                          strokeWidth="8" strokeDasharray={`${wScore * 2.83} 283`} strokeLinecap="round" />
                </svg>
                <div className="score-text">{wScore.toFixed(1)}%<br/><span className="score-label">Score</span></div>
              </div>
              <span className={`badge ${wScore >= 75 ? 'badge-success' : 'badge-danger'}`}>
                {wScore >= 75 ? 'Atende' : 'Não Atende'}
              </span>
            </>
          ) : (
            <div className="flex-col gap-2 w-full pt-4">
              <div className="alert alert-warning mb-2 justify-center">Carga horária não identificada no PDF/Texto</div>
              {isCoord && (
                <>
                  {!data.workload.ufsm && <input type="number" className="form-input text-center" placeholder="CH UFSM" value={ufsmCh} onChange={e=>setUfsmCh(e.target.value)} />}
                  {!data.workload.externo && <input type="number" className="form-input text-center" placeholder="CH Externa" value={extCh} onChange={e=>setExtCh(e.target.value)} />}
                  <button className="btn btn-primary w-full mt-2" onClick={handleUpdateCH} disabled={!ufsmCh && !extCh}>Calcular CH Manualmente</button>
                </>
              )}
            </div>
          )}
        </div>
      </div>

      {reusable.length > 0 && (
        <div className="alert alert-info mb-4">
          <strong>Aviso de Histórico:</strong> Esta equivalência baseou-se em {reusable.length} análise(s) anterior(es) já processada(s).
        </div>
      )}

      {data.alertas?.map((a: any, i: number) => (
         <div key={i} className={`alert alert-${a.nivel === 'error' ? 'error' : 'warning'} mb-2`}>
           <strong>Aviso:</strong> {a.mensagem}
         </div>
      ))}

      <div className="card mt-4">
        <h3 className="card-title">Detalhamento Técnico (Similaridade)</h3>
        <div className="table-wrapper mt-3">
          <table>
            <thead>
              <tr>
                <th style={{ width: '45%' }}>Tópico UFSM</th>
                <th style={{ width: '40%' }}>Melhor Correspondência Externa</th>
                <th>Classificação</th>
                <th>Score</th>
              </tr>
            </thead>
            <tbody>
              {data.matches?.map((m: any, i: number) => (
                <tr key={i}>
                  <td>{m.ufsm_item}</td>
                  <td className="text-muted">{m.externo_item || '-'}</td>
                  <td>
                    <span className={`badge ${
                      m.classificacao === 'equivalente' ? 'badge-success' : 
                      m.classificacao === 'parcialmente_equivalente' ? 'badge-warning' : 'badge-danger'
                    }`}>
                      {m.classificacao.replace('_', ' ')}
                    </span>
                  </td>
                  <td className="font-bold">{m.score_final.toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
