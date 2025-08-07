import { NovelTask } from '../types/novelTask';
import { showError, showNetworkError } from '../store/toastStore';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/api/v1/ws';
const REQUEST_TIMEOUT = 10000; // 10 seconds

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
  private async fetchWithTimeout(url: string, options: RequestInit = {}): Promise<Response> {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), REQUEST_TIMEOUT);

    try {
      const response = await fetch(url, {
        ...options,
        signal: controller.signal,
      });
      clearTimeout(timeout);
      return response;
    } catch (error: any) {
      clearTimeout(timeout);
      if (error.name === 'AbortError') {
        showError('请求超时', '服务器响应时间过长，请稍后重试');
        throw new Error('Request timeout');
      }
      if (error.message === 'Failed to fetch') {
        showNetworkError();
        throw new Error('Network error');
      }
      throw error;
    }
  }

  async uploadFile(file: File): Promise<NovelTask> {
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await this.fetchWithTimeout(`${API_URL}/tasks/upload`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Upload failed' }));
        showError('上传失败', error.detail || '文件上传失败，请重试');
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
    } catch (error: any) {
      if (!error.message.includes('Network error') && !error.message.includes('timeout')) {
        showError('上传失败', error.message);
      }
      throw error;
    }
  }

  async getTasks(
    page: number = 1,
    pageSize: number = 20,
    status?: string,
    sortBy: string = 'uploaded_at'
  ): Promise<TaskListResponse> {
    try {
      const params = new URLSearchParams({
        page: page.toString(),
        page_size: pageSize.toString(),
        sort_by: sortBy,
        order: 'desc',
      });

      if (status && status !== 'all') {
        params.append('status', status);
      }

      const response = await this.fetchWithTimeout(`${API_URL}/tasks?${params}`);
      
      if (!response.ok) {
        showError('获取任务列表失败', '无法加载任务列表，请刷新页面');
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
    } catch (error: any) {
      if (!error.message.includes('Network error') && !error.message.includes('timeout')) {
        showError('加载失败', error.message);
      }
      throw error;
    }
  }

  async getTask(taskId: string): Promise<NovelTask> {
    try {
      const response = await this.fetchWithTimeout(`${API_URL}/tasks/${taskId}`);
      
      if (!response.ok) {
        showError('获取任务失败', '无法获取任务详情');
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
    } catch (error: any) {
      if (!error.message.includes('Network error') && !error.message.includes('timeout')) {
        showError('获取失败', error.message);
      }
      throw error;
    }
  }

  async deleteTask(taskId: string): Promise<void> {
    try {
      const response = await this.fetchWithTimeout(`${API_URL}/tasks/${taskId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        showError('删除失败', '无法删除任务，请重试');
        throw new Error('Failed to delete task');
      }
    } catch (error: any) {
      if (!error.message.includes('Network error') && !error.message.includes('timeout')) {
        showError('删除失败', error.message);
      }
      throw error;
    }
  }

  async retryTask(taskId: string): Promise<NovelTask> {
    try {
      const response = await this.fetchWithTimeout(`${API_URL}/tasks/${taskId}/retry`, {
        method: 'POST',
      });

      if (!response.ok) {
        showError('重试失败', '无法重试任务，请稍后再试');
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
    } catch (error: any) {
      if (!error.message.includes('Network error') && !error.message.includes('timeout')) {
        showError('重试失败', error.message);
      }
      throw error;
    }
  }

  async getStatistics(): Promise<TaskStatistics> {
    try {
      const response = await this.fetchWithTimeout(`${API_URL}/tasks/statistics`);
      
      if (!response.ok) {
        throw new Error('Failed to fetch statistics');
      }

      return response.json();
    } catch (error: any) {
      // Statistics failure is not critical, don't show error toast
      console.error('Failed to fetch statistics:', error);
      throw error;
    }
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
      showError('连接错误', 'WebSocket连接出现问题');
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