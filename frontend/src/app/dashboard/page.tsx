'use client';
import { useState, useEffect } from 'react';
import Link from 'next/link';
import { getAnalyses } from '@/lib/api';

export default function Dashboard() {
  const [analyses, setAnalyses] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchAnalyses();
  }, []);

  const fetchAnalyses = async () => {
    try {
      setLoading(true);
      const data = await getAnalyses();
      setAnalyses(data || []);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Erro ao carregar análises');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mt-10">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Painel de Coordenação</h1>
        <button onClick={fetchAnalyses} className="btn btn-outline btn-sm">🔄 Atualizar</button>
      </div>

      <div className="card">
        <h2 className="card-title text-xl mb-4">Análises e Solicitações Pendentes</h2>
        
        {loading ? (
          <div className="flex justify-center p-10"><div className="spinner"></div></div>
        ) : error ? (
          <div className="alert alert-error">{error}</div>
        ) : analyses.length === 0 ? (
          <div className="text-center p-10 text-muted">Nenhuma análise pendente no momento.</div>
        ) : (
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>UFSM (Destino)</th>
                  <th>Origem (Externa)</th>
                  <th>Scores (C / CH)</th>
                  <th>Status Técnico</th>
                  <th>Ações</th>
                </tr>
              </thead>
              <tbody>
                {analyses.map(a => (
                  <tr key={a.id}>
                    <td className="text-xs font-mono">{a.id.substring(0, 8)}...</td>
                    <td>{a.ufsm_program_id}</td>
                    <td>
                        {a.external_program_id ? a.external_program_id : (a.external_program_ids ? `${a.external_program_ids.length} disciplinas` : 'N/A')}
                    </td>
                    <td>
                        <span className={`badge ${a.content_score >= 75 ? 'badge-success' : 'badge-warning'}`}>{a.content_score != null ? Math.round(a.content_score) : 0}%</span>
                        <span className="badge badge-info ml-1">{a.workload_score != null ? Math.round(a.workload_score) + '%' : 'S/ CH'}</span>
                    </td>
                    <td>
                        <span className={`text-sm font-bold ${a.resultado_tecnico === 'EQUIVALENTE' ? 'text-success' : 'text-warning'}`}>
                            {a.resultado_tecnico}
                        </span>
                    </td>
                    <td>
                      {a.resultado_tecnico === 'PENDENTE_DADOS' ? (
                        <Link href={`/certifications?analysis_id=${a.id}`} className="btn btn-warning btn-sm">
                          Completar Dados
                        </Link>
                      ) : (
                        <Link href={`/certifications?analysis_id=${a.id}`} className="btn btn-primary btn-sm">
                          Certificar
                        </Link>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
