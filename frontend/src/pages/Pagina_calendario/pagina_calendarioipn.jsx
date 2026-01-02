import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ChevronLeft, LogOut, User, ExternalLink, Calendar } from 'lucide-react';
import "./pagina_calendarioipn.css";

// RUTA AL ARCHIVO LOCAL
const PDF_LOCAL = "/calendario.pdf";

// RUTA ORIGINAL
const PDF_ONLINE = "https://www.ipn.mx/assets/files/main/docs/calendario-escolarizada-2024-2025.pdf";

const CalendarioIPN = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkUserSession();
    setTimeout(() => setLoading(false), 500); 
  }, []);

  const checkUserSession = () => {
      const token = localStorage.getItem('token');
      if (token) {
          const savedName = localStorage.getItem('user_full_name') || "Estudiante";
          setUser({ name: savedName.split(' ')[0] });
      }
  };

  const handleLogout = () => {
      localStorage.removeItem('token');
      localStorage.removeItem('user_full_name');
      setUser(null);
      navigate('/login');
  };

  return (
    <div className="page-container">
      
      <header className="fixed-header">
        <div className="header-left">
            <button onClick={() => navigate('/horarios')} className="btn-back-outline">
                <ChevronLeft size={20}/> Volver
            </button>
        </div>
        <h1 className="page-title">Calendario IPN</h1>
        <div className="header-right">
            {user ? (
                <div className="user-widget-mini">
                    <span>Hola, <strong>{user.name}</strong></span>
                    <button onClick={handleLogout} className="logout-mini" title="Salir"><LogOut size={14}/></button>
                </div>
            ) : (
                <Link to="/login" className="login-btn-mini"><User size={14}/> Entrar</Link>
            )}
        </div>
      </header>

      <main className="calendar-content">
        
        {/* 1. Botón superior discreto a la derecha */}
        <div className="top-actions-bar">
            <a href={PDF_ONLINE} target="_blank" rel="noreferrer" className="btn-action-filled">
                <ExternalLink size={16}/> Abrir en pestaña nueva
            </a>
        </div>

        {/* 2. Visor de PDF (Protagonista) */}
        <div className="pdf-viewer-container">
            {loading ? (
                <div className="loading-spinner">
                    <div className="spinner"></div>
                    <p>Cargando calendario...</p>
                </div>
            ) : (
                <iframe 
                    src={PDF_LOCAL} 
                    title="Calendario IPN"
                    className="pdf-frame"
                    type="application/pdf"
                />
            )}
        </div>

        {/* 3. Información abajo y pequeña */}
        <div className="calendar-footer-info">
            <Calendar className="icon-blue-small" size={18}/>
            <div className="info-text">
                <h3>Modalidad Escolarizada</h3>
                <span>Ciclo Escolar 2024 - 2025</span>
            </div>
        </div>

      </main>

      <footer className="footer-bar">
        <Link to="/menu"><button className="btn-volver">Volver al menú principal</button></Link>
      </footer>

    </div>
  );
};

export default CalendarioIPN;