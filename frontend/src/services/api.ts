import { NovelTask } from '../types/novelTask';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/api/v1/ws';

export interface TaskListResponse {
  tasks: NovelTask[];
  total: number;
  page: number;
  page_size: number;
}

export interface TaskStatistics {
  total: number;
  pending: number;
  processing: number;
  completed: number;
  failed: number;
  avg_processing_time_ms?: number;
  success_rate?: number;
}

class ApiService {
  async uploadFile(file: File): Promise<NovelTask> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_URL}/tasks/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Upload failed');
    }

    const data = await response.json();
    
    // Transform API response to match frontend model
    return {
      id: data.task_id,
      fileName: data.file_name,
      fileSize: data.file_size,
      status: data.status,
      progress: 0,
      uploadedAt: new Date(),
    };
  }

  async getTasks(
    page: number = 1,
    pageSize: number = 20,
    status?: string,
    sortBy: string = 'uploaded_at'
  ): Promise<TaskListResponse> {
    const params = new URLSearchParams({
      page: page.toString(),
      page_size: pageSize.toString(),
      sort_by: sortBy,
      order: 'desc',
    });

    if (status && status !== 'all') {
      params.append('status', status);
    }

    const response = await fetch(`${API_URL}/tasks?${params}`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch tasks');
    }

    const data = await response.json();
    
    // Transform tasks to match frontend model
    const tasks = data.tasks.map((task: any) => ({
      id: task.id,
      fileName: task.file_name,
      fileSize: task.file_size,
      status: task.status,
      progress: task.progress,
      uploadedAt: new Date(task.uploaded_at),
      startedAt: task.started_at ? new Date(task.started_at) : undefined,
      completedAt: task.completed_at ? new Date(task.completed_at) : undefined,
      resultUrl: task.result_url,
      error: task.error_message,
    }));

    return {
      tasks,
      total: data.total,
      page: data.page,
      page_size: data.page_size,
    };
  }

  async getTask(taskId: string): Promise<NovelTask> {
    const response = await fetch(`${API_URL}/tasks/${taskId}`);
    
    if (!response.ok) {
      throw new Error('Task not found');
    }

    const task = await response.json();
    
    return {
      id: task.id,
      fileName: task.file_name,
      fileSize: task.file_size,
      status: task.status,
      progress: task.progress,
      uploadedAt: new Date(task.uploaded_at),
      startedAt: task.started_at ? new Date(task.started_at) : undefined,
      completedAt: task.completed_at ? new Date(task.completed_at) : undefined,
      resultUrl: task.result_url,
      error: task.error_message,
    };
  }

  async deleteTask(taskId: string): Promise<void> {
    const response = await fetch(`${API_URL}/tasks/${taskId}`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      throw new Error('Failed to delete task');
    }
  }

  async retryTask(taskId: string): Promise<NovelTask> {
    const response = await fetch(`${API_URL}/tasks/${taskId}/retry`, {
      method: 'POST',
    });

    if (!response.ok) {
      throw new Error('Failed to retry task');
    }

    const task = await response.json();
    
    return {
      id: task.id,
      fileName: task.file_name,
      fileSize: task.file_size,
      status: task.status,
      progress: task.progress,
      uploadedAt: new Date(task.uploaded_at),
      startedAt: task.started_at ? new Date(task.started_at) : undefined,
      completedAt: task.completed_at ? new Date(task.completed_at) : undefined,
      resultUrl: task.result_url,
      error: task.error_message,
    };
  }

  async getStatistics(): Promise<TaskStatistics> {
    const response = await fetch(`${API_URL}/tasks/statistics`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch statistics');
    }

    return response.json();
  }

  connectWebSocket(clientId: string, onMessage: (data: any) => void): WebSocket {
    const ws = new WebSocket(`${WS_URL}/tasks/${clientId}`);
    
    ws.onopen = () => {
      console.log('WebSocket connected');
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      onMessage(data);
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
    };

    return ws;
  }

  subscribeToTask(ws: WebSocket, taskId: string) {
    if (ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({
        type: 'subscribe',
        task_id: taskId,
      }));
    }
  }

  unsubscribeFromTask(ws: WebSocket, taskId: string) {
    if (ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({
        type: 'unsubscribe',
        task_id: taskId,
      }));
    }
  }
}

export const apiService = new ApiService();