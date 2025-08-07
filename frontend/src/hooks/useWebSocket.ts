import { useEffect, useRef } from 'react';
import { config } from '../config';
import { useTaskStore } from '../store/novelTaskStore';

export const useWebSocket = () => {
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<number | null>(null);
  const clientId = useRef(`client-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`);
  
  const updateTaskStatus = useTaskStore((state) => state.updateTaskStatus);
  const updateTaskProgress = useTaskStore((state) => state.updateTaskProgress);

  const connect = () => {
    if (config.USE_MOCK_API) {
      return; // Skip WebSocket in mock mode
    }

    try {
      const ws = new WebSocket(`${config.WS_URL}/tasks/${clientId.current}`);
      
      ws.onopen = () => {
        console.log('WebSocket connected');
        wsRef.current = ws;
        
        // Clear reconnect timeout
        if (reconnectTimeoutRef.current) {
          window.clearTimeout(reconnectTimeoutRef.current);
          reconnectTimeoutRef.current = null;
        }
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          if (data.type === 'task_update') {
            updateTaskStatus(
              data.task_id,
              data.status,
              data.result_url,
              data.error_message
            );
            
            if (data.progress !== undefined) {
              updateTaskProgress(data.task_id, data.progress);
            }
          }
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
      };

      ws.onclose = () => {
        console.log('WebSocket disconnected');
        wsRef.current = null;
        
        // Attempt to reconnect after 3 seconds
        reconnectTimeoutRef.current = window.setTimeout(() => {
          console.log('Attempting to reconnect WebSocket...');
          connect();
        }, 3000);
      };
    } catch (error) {
      console.error('Failed to connect WebSocket:', error);
    }
  };

  const disconnect = () => {
    if (reconnectTimeoutRef.current) {
      window.clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
  };

  const subscribeToTask = (taskId: string) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'subscribe',
        task_id: taskId,
      }));
    }
  };

  const unsubscribeFromTask = (taskId: string) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'unsubscribe',
        task_id: taskId,
      }));
    }
  };

  useEffect(() => {
    connect();
    
    return () => {
      disconnect();
    };
  }, []);

  return {
    subscribeToTask,
    unsubscribeFromTask,
    isConnected: wsRef.current?.readyState === WebSocket.OPEN,
  };
};