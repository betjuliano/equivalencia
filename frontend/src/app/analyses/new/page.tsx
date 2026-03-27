'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import ProgramInput from '@/components/ProgramInput';
import { createAnalysis } from '@/lib/api';

export default function NewAnalysis() {
  const router = useRouter();
  const [ufsmId, setUfsmId] = useState<string | null>(null);
  const [extId, setExtId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleCreate = async () => {
    if (!ufsmId || !extId) return;
    setLoading(true);
    try {
      const res = await createAnalysis({
        ufsm_program_id: ufsmId,
        external_program_id: extId,
      });
      router.push(`/analyses/${res.analysis_id}`);
    } catch (err: any) {
      alert(err.message || 'Erro ao comparar programas');
      setLoading(false);
    }
  };

  return (
    <div className="container page-content fade-in">
      <div className="flex items-center justify-between mb-3">
        <h1 className="text-2xl font-bold">Nova Análise de Equivalência</h1>
        {ufsmId && extId && (
          <button className="btn btn-success fade-in" onClick={handleCreate} disabled={loading}>
            {loading ? 'Comparando...' : '➔ Iniciar Comparação Técnica'}
          </button>
        )}
      </div>

      <div className="two-col" style={{ height: 'calc(100vh - 180px)' }}>
        <div className="flex-col gap-2">
          {!ufsmId ? (
            <ProgramInput tipo="ufsm" title="📚 Disciplina UFSM (Destino)" 
              onProgramCreated={(id) => setUfsmId(id)} />
          ) : (
            <div className="card h-full flex flex-col items-center justify-center fade-in">
              <div className="score-ring mb-2" style={{ width: '80px', height: '80px' }}>
                <span className="text-4xl">✅</span>
              </div>
              <h3 className="font-bold">Disciplina UFSM Carregada</h3>
              <p className="text-sm text-dim">{ufsmId}</p>
              <button className="btn btn-outline btn-sm mt-3" onClick={() => setUfsmId(null)}>Trocar</button>
            </div>
          )}
        </div>

        <div className="flex-col gap-2">
          {!extId ? (
            <ProgramInput tipo="externo" title="📄 Disciplina de Origem (Externa)" 
              onProgramCreated={(id) => setExtId(id)} />
          ) : (
            <div className="card h-full flex flex-col items-center justify-center fade-in">
              <div className="score-ring mb-2" style={{ width: '80px', height: '80px' }}>
                <span className="text-4xl">✅</span>
              </div>
              <h3 className="font-bold">Disciplina Externa Carregada</h3>
              <p className="text-sm text-dim">{extId}</p>
              <button className="btn btn-outline btn-sm mt-3" onClick={() => setExtId(null)}>Trocar</button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
