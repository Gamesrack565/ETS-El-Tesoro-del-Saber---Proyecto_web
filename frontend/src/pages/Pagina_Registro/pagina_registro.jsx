import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import api from '../../api/axiosConfig'; // Asegúrate de importar tu configuración de axios
import './pagina_registro.css';

function RegisterPage() {
  const navigate = useNavigate();
  
  // Estado para los datos del formulario
  const [formData, setFormData] = useState({
    full_name: '',
    career: '',
    email: '',
    password: ''
  });

  const [error, setError] = useState('');

  // Manejar cambios en los inputs
  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  // Enviar datos al Backend
  const handleRegister = async (e) => {
    e.preventDefault(); // Evitar recarga de página
    setError('');

    // Validación básica
    if (!formData.full_name || !formData.career || !formData.email || !formData.password) {
      setError("Por favor completa todos los campos.");
      return;
    }

    try {
      // Ajusta la ruta '/users/register' según como hayas definido el prefix en main.py
      // Si en main.py es app.include_router(user_router, prefix="/users")...
      await api.post('/users/register', formData);
      
      alert("¡Registro exitoso! Ahora inicia sesión.");
      navigate('/login');

    } catch (err) {
      console.error(err);
      // Mostrar el error que viene del backend (ej: "El email ya está registrado")
      if (err.response && err.response.data) {
        setError(err.response.data.detail);
      } else {
        setError("Ocurrió un error al intentar registrarse.");
      }
    }
  };

  return (
    <div className="auth-container">
      <div className="user-icon">
        <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1" strokeLinecap="round" strokeLinejoin="round">
          <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
          <circle cx="12" cy="7" r="4" />
        </svg>
      </div>

      <p className="auth-subtitle">Crea tu cuenta para acceder al Tesoro del Saber</p>

      <form className="auth-form" onSubmit={handleRegister}>
        
        {/* Nombre Completo */}
        <label htmlFor="full_name">Nombre Completo</label>
        <input 
          type="text" 
          id="full_name" 
          name="full_name"
          placeholder="Ej. Juan Pérez" 
          value={formData.full_name}
          onChange={handleChange}
        />

        {/* Carrera */}
        <label htmlFor="career">Carrera</label>
        <input 
          type="text" 
          id="career" 
          name="career"
          placeholder="Ej. Ingeniería en Sistemas, IA, ISC, etc..." 
          value={formData.career}
          onChange={handleChange}
        />

        {/* Correo */}
        <label htmlFor="email">Correo</label>
        <input 
          type="email" 
          id="email" 
          name="email"
          placeholder="correo@gmail.com" 
          value={formData.email}
          onChange={handleChange}
        />

        {/* Contraseña */}
        <label htmlFor="password">Contraseña</label>
        <input 
          type="password" 
          id="password" 
          name="password"
          placeholder="Mínimo 8 caracteres" 
          value={formData.password}
          onChange={handleChange}
        />

        {/* Mensaje de Error */}
        {error && <div className="error-msg">{error}</div>}

        <button type="submit" className="btn btn-primary">Registrarme</button>

        <Link to="/login" className="btn btn-secondary">
          Ya tengo una cuenta
        </Link>

      </form>
    </div>
  );
}

export default RegisterPage;