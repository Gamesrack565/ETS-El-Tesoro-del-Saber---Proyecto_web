import axios from 'axios';

const api = axios.create({
  baseURL: 'inclined-gwenette-el-tesoro-del-saber-c25d78f1.koyeb.app',
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