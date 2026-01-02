import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../api/axiosConfig';
import './pagina_menu.css';

// Importación de iconos (asegúrate de que las rutas sigan bien)
import iconResenas from '../../assets/icono_resenas.png';
import iconPortal from '../../assets/icono_portal.png';
import iconAsistente from '../../assets/icono_asistente.png';
import iconHorarios from '../../assets/icono_horarios.png';
import iconAnalisis from '../../assets/icono_analisis.png'; 

const Pagina_Menu = () => {
    const [usuario, setUsuario] = useState(null);
    const navigate = useNavigate();

    useEffect(() => {
        const fetchUserData = async () => {
            try {
                const response = await api.get('/users/me');
                setUsuario(response.data);
            } catch (error) {
                console.error("Error al obtener datos:", error);
                if (error.response && error.response.status === 401) {
                    navigate('/login');
                }
            }
        };
        fetchUserData();
    }, [navigate]);

    return (
        // 1. NUEVO WRAPPER PRINCIPAL
        <div className="page-wrapper">
            
            {/* --- NUEVO BOTÓN DE REGRESO --- */}
            {/* Usamos absolute en CSS para pegarlo a la izquierda */}
            <button className="btn-back" onClick={() => navigate('/')}>
                ← Inicio
            </button>

            {/* 2. CONTENEDOR DE CONTENIDO (Título y Grid) */}
            <div className="menu-content">
                <h1 className="menu-title">
                    {usuario ? `¡Hola, ${usuario.full_name.split(' ')[0]}!` : 'Cargando...'}
                </h1>
                
                {usuario && <p className="menu-subtitle">Bienvenido al Tesoro del Saber</p>}

                <div className="menu-grid">
                    {/* Reseñas */}
                    <div className="menu-item" onClick={() => navigate('/resenas')}>
                        <div className="icon-box">
                            <img src={iconResenas} alt="Reseñas" className="menu-icon" />
                        </div>
                        <p>Reseñas de Profesores</p>
                    </div>

                    {/* Portal */}
                    <div className="menu-item" onClick={() => navigate('/portal')}>
                        <div className="icon-box">
                            <img src={iconPortal} alt="Portal" className="menu-icon" />
                        </div>
                        <p>Portal Estudiantil</p>
                    </div>

                    {/* Análisis */}
                    <div className="menu-item" onClick={() => navigate('/analisis')}>
                        <div className="icon-box">
                            <img src={iconAnalisis} alt="Análisis" className="menu-icon" />
                        </div>
                        <p>Análisis de mensajes</p>
                    </div>

                    {/* Asistente */}
                    <div className="menu-item" onClick={() => navigate('/asistente')}>
                        <div className="icon-box">
                            <img src={iconAsistente} alt="Asistente" className="menu-icon" />
                        </div>
                        <p>Asistente Virtual</p>
                    </div>

                    {/* Horarios */}
                    <div className="menu-item" onClick={() => navigate('/horarios')}>
                        <div className="icon-box">
                            <img src={iconHorarios} alt="Horarios" className="menu-icon" />
                        </div>
                        <p>Horarios y Calendario</p>
                    </div>
                </div>
            </div>

            {/* 3. EL RECTÁNGULO AZUL (FOOTER) */}
            <footer className="menu-footer">
                <p>ETS - El Tesoro del Saber</p>
            </footer>
        </div>
    );
};

export default Pagina_Menu;