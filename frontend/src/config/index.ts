export const config = {
  API_URL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
  WS_URL: import.meta.env.VITE_WS_URL || 'ws://localhost:8000/api/v1/ws',
  USE_MOCK_API: import.meta.env.VITE_USE_MOCK_API === 'true' || false,
  MAX_FILE_SIZE: parseInt(import.meta.env.VITE_MAX_FILE_SIZE || '10485760'),
  ALLOWED_EXTENSIONS: (import.meta.env.VITE_ALLOWED_EXTENSIONS || '.txt,.md').split(','),
};