'use client';
import { useState } from 'react';
import { login } from '@/lib/api';

export default function Login() {
  const [user, setUser] = useState('');
  const [pass, setPass] = useState('');
  const [err, setErr] = useState('');

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await login(user, pass);
      window.location.href = '/';
    } catch (error: any) {
      setErr(error.message || 'Erro ao logar');
    }
  };

  return (
    <div className="container" style={{ maxWidth: '400px', margin: '4rem auto' }}>
      <div className="card">
        <div style={{ textAlign: 'center', fontSize: '3rem', marginBottom: '1rem' }}>📖</div>
        <h2 className="card-title" style={{ justifyContent: 'center', marginBottom: '0.5rem' }}>S.ADM</h2>
        <p className="text-center text-muted text-sm mb-3">Acesso restrito à Coordenação de Curso</p>
        
        {err && <div className="alert alert-error">{err}</div>}
        
        <form onSubmit={handleLogin}>
          <div className="form-group">
            <label className="form-label">Usuário Moodle/UFSM</label>
            <input 
              type="text" className="form-input" 
              value={user} onChange={e => setUser(e.target.value)} 
              placeholder="ex: coord" required
            />
          </div>
          <div className="form-group">
            <label className="form-label">Senha</label>
            <input 
              type="password" className="form-input" 
              value={pass} onChange={e => setPass(e.target.value)} 
              placeholder="••••••••" required
            />
          </div>
          <button type="submit" className="btn btn-primary w-full mt-2">Entrar</button>
        </form>

        <div className="text-center mt-4 border-t border-border pt-4">
          <p className="text-xs text-muted">Acesso exclusivo para deferimento de certificações. Alunos não necessitam de login para solicitar equivalências.</p>
        </div>
      </div>
    </div>
  );
}
