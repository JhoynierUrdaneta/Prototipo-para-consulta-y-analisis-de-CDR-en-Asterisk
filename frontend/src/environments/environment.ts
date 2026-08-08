// La API se sirve siempre bajo el mismo origen: en desarrollo lo resuelve
// proxy.conf.json y en producción nginx (ver nginx.conf, location /api/).
export const environment = {
  apiUrl: '/api',
};
