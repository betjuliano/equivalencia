'use client';
import Link from 'next/link';
import { useEffect, useState } from 'react';
import { clearToken, getToken } from '@/lib/api';

export default function Navbar() {
  const [logged, setLogged] = useState(false);
  useEffect(() => { setLogged(!!getToken()); }, []);

  return (
    <nav className="navbar">
      <Link href="/" className="navbar-brand">
        <span className="logo">🎓</span>
        <span>Equivale UFSM</span>
      </Link>
      <div className="navbar-links">
        <Link href="/">Início</Link>
        {logged ? (
          <>
            <Link href="/analyses/new" className="text-warning">Painel Coordenação</Link>
            <button
              className="btn btn-outline btn-sm"
              onClick={() => { clearToken(); setLogged(false); window.location.href = '/'; }}
            >Sair</button>
          </>
        ) : (
          <Link href="/login" className="btn btn-primary btn-sm">Acesso Coordenação</Link>
        )}
      </div>
    </nav>
  );
}
