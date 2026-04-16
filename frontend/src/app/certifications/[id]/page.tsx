'use client';
import { use, useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { getAnalysis, certify, getCertification } from '@/lib/api';

export default function Certification({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const router = useRouter();
  const searchParams = useSearchParams();
  const isCreate = searchParams.get('create') === 'true';
  
  const [data, setData] = useState<any>(null);
  const [cert, setCert] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  // Form
  const [decisao, setDecisao] = useState('deferida');
  const [ressalvas, setRessalvas] = useState('');
  const [publicar, setPublicar] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    async function load() {
      try {
        if (isCreate) {
          const res = await getAnalysis(id);
          setData(res);
        } else {
          const res = await getCertification(id);
          setCert(res);
        }
      } catch { alert('Erro ao carregar'); }
      finally { setLoading(false); }
    }
    load();
  }, [id, isCreate]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      if (!data) return;
      await certify({
        analysis_id: id,
        decisao,
        ressalvas,
        publicavel_para_consulta: publicar,
        status: decisao === 'deferida' ? 'certificada' : 'indeferida',
        curso: data.curso || "Administração", 
        disciplina_ufsm_nome: data.ufsm_program_name || data.ufsm_program_id,
        instituicao_origem: data.external_institution || "Instituição Externa",
        disciplina_origem_nome: data.external_program_name || data.external_program_id,
      });
      alert('Certificação salva com sucesso!');
      router.push('/');
    } catch (err: any) { alert(err.message || 'Erro'); }
    finally { setSubmitting(false); }
  };

  if (loading) return <div className="loading-overlay"><div className="spinner"></div></div>;

  if (isCreate) {
    if (!data) return <div>Erro ao carregar análise.</div>;
    return (
      <div className="container page-content fade-in" style={{ maxWidth: 600 }}>
        <h1 className="text-2xl font-bold mb-3">Certificar Equivalência</h1>
        
        <div className="card mb-3">
          <h3 className="card-title">Resumo da Análise Técnica</h3>
          <p><strong>Conteúdo:</strong> {data.content_score?.toFixed(1)}%</p>
          <p><strong>Carga Horária:</strong> {data.workload_score?.toFixed(1)}%</p>
          <p><strong>Parecer Algoritmo:</strong> {data.resultado_tecnico}</p>
        </div>

        <form className="card" onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Decisão da Coordenação</label>
            <select className="form-select" value={decisao} onChange={e=>setDecisao(e.target.value)}>
              <option value="deferida">Deferida (Certificar Equivalência)</option>
              <option value="indeferida">Indeferida (Não Equivalente)</option>
              <option value="complementacao">Solicitar Complementação</option>
            </select>
          </div>
          
          <div className="form-group">
            <label className="form-label">Ressalvas ou Observações (Opcional)</label>
            <textarea className="form-textarea" style={{minHeight: 100}} value={ressalvas} onChange={e=>setRessalvas(e.target.value)} />
          </div>

          <div className="form-group flex justify-between items-center" style={{ marginBottom: '1.5rem', background: 'var(--bg)', padding: '1rem', borderRadius: 8 }}>
            <label className="form-label" style={{ marginBottom: 0 }}>Publicar para Consulta Pública de Estudantes</label>
            <input type="checkbox" checked={publicar} onChange={e=>setPublicar(e.target.checked)} style={{transform: 'scale(1.5)'}} />
          </div>

          <button type="submit" className="btn btn-success w-full" disabled={submitting}>
            {submitting ? 'Assinando e Salvando...' : 'Assinar Digitalmente e Certificar'}
          </button>
        </form>
      </div>
    );
  }

  // Visualization mode (View Certification)
  if (!cert) return <div>Certificação não encontrada.</div>;
  return (
    <div className="container page-content fade-in" style={{ maxWidth: 600 }}>
      <div className="card">
        <h1 className="text-xl font-bold mb-4">Certificado de Equivalência</h1>
        <div className="alert alert-success mt-2 mb-3">Equivalência certificada e válida.</div>
        <p><strong>Curso:</strong> {cert.curso}</p>
        <div className="divider" />
        <p><strong>UFSM:</strong> {cert.disciplina_ufsm_nome} ({cert.disciplina_ufsm_codigo})</p>
        <p><strong>Origem:</strong> {cert.disciplina_origem_nome} ({cert.instituicao_origem})</p>
        <div className="divider" />
        <p><strong>Data:</strong> {new Date(cert.data_certificacao).toLocaleDateString()}</p>
        <p><strong>Certificado por:</strong> Coordenação de Curso</p>
        {cert.ressalvas && <p className="mt-2 text-warning"><strong>Ressalvas:</strong> {cert.ressalvas}</p>}
      </div>
    </div>
  );
}
