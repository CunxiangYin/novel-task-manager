import React, { useEffect, useState } from 'react';
import { WifiOff } from 'lucide-react';

export const ConnectionStatus: React.FC = () => {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [backendAvailable, setBackendAvailable] = useState(true);

  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    // Check backend availability
    const checkBackend = async () => {
      try {
        const controller = new AbortController();
        const timeout = setTimeout(() => controller.abort(), 3000);
        
        const response = await fetch(
          `${import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'}/tasks/statistics`,
          { signal: controller.signal }
        );
        
        clearTimeout(timeout);
        setBackendAvailable(response.ok);
      } catch {
        setBackendAvailable(false);
      }
    };

    // Check backend initially and every 30 seconds
    checkBackend();
    const interval = setInterval(checkBackend, 30000);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
      clearInterval(interval);
    };
  }, []);

  if (!isOnline) {
    return (
      <div className="fixed bottom-4 left-4 bg-red-500 text-white px-4 py-2 rounded-lg shadow-lg flex items-center gap-2 z-50">
        <WifiOff className="w-5 h-5" />
        <span>无网络连接</span>
      </div>
    );
  }

  if (!backendAvailable) {
    return (
      <div className="fixed bottom-4 left-4 bg-orange-500 text-white px-4 py-2 rounded-lg shadow-lg flex items-center gap-2 z-50">
        <WifiOff className="w-5 h-5" />
        <span>后端服务不可用</span>
      </div>
    );
  }

  return null;
};