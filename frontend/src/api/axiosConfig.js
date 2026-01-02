import axios from 'axios';

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000/api',
});

// === MAGIA AQUÍ ===
// Interceptor: Antes de que salga cualquier petición, ejecuta esto:
api.interceptors.request.use(
  (config) => {
    // 1. Buscamos si hay un token guardado
    const token = localStorage.getItem('token');
    
    // 2. Si hay token, lo agregamos al encabezado como 'Bearer <token>'
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export default api;