import { create } from 'zustand';
import { NovelTask } from '../types/novelTask';

interface TaskStore {
  tasks: NovelTask[];
  addTask: (file: File, taskFromBackend?: NovelTask) => string;
  updateTaskProgress: (id: string, progress: number) => void;
  updateTaskStatus: (id: string, status: NovelTask['status'], resultUrl?: string, error?: string) => void;
  removeTask: (id: string) => void;
  getTask: (id: string) => NovelTask | undefined;
  simulateProgress: (id: string) => void;
  processNextTask: () => void;
}

const MAX_CONCURRENT_TASKS = 3;

export const useTaskStore = create<TaskStore>((set, get) => ({
  tasks: [],
  
  addTask: (file: File, taskFromBackend?: NovelTask) => {
    // 如果有后端返回的任务信息，使用它；否则创建本地任务
    const newTask: NovelTask = taskFromBackend || {
      id: `task-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      fileName: file.name,
      fileSize: file.size,
      status: 'pending',
      progress: 0,
      uploadedAt: new Date(),
    };
    
    set((state) => ({
      tasks: [newTask, ...state.tasks],
    }));
    
    // 如果任务来自后端且状态是 pending，不需要模拟处理
    // 后端会通过 WebSocket 发送真实的进度更新
    if (!taskFromBackend) {
      // 只有本地模拟任务才需要调用 processNextTask
      get().processNextTask();
    }
    
    return newTask.id;
  },
  
  processNextTask: () => {
    const state = get();
    const processingCount = state.tasks.filter(t => t.status === 'processing').length;
    
    if (processingCount < MAX_CONCURRENT_TASKS) {
      const nextTask = state.tasks.find(t => t.status === 'pending');
      if (nextTask) {
        setTimeout(() => {
          get().updateTaskStatus(nextTask.id, 'processing');
          get().simulateProgress(nextTask.id);
        }, 500);
      }
    }
  },
  
  updateTaskProgress: (id: string, progress: number) => {
    set((state) => ({
      tasks: state.tasks.map((task) =>
        task.id === id
          ? { ...task, progress: Math.min(100, Math.max(0, progress)) }
          : task
      ),
    }));
  },
  
  updateTaskStatus: (id: string, status: NovelTask['status'], resultUrl?: string, error?: string) => {
    set((state) => ({
      tasks: state.tasks.map((task) =>
        task.id === id
          ? {
              ...task,
              status,
              startedAt: status === 'processing' ? new Date() : task.startedAt,
              completedAt: status === 'completed' || status === 'failed' ? new Date() : task.completedAt,
              resultUrl: resultUrl || task.resultUrl,
              error: error || task.error,
            }
          : task
      ),
    }));
  },
  
  removeTask: (id: string) => {
    set((state) => ({
      tasks: state.tasks.filter((task) => task.id !== id),
    }));
  },
  
  getTask: (id: string) => {
    return get().tasks.find((task) => task.id === id);
  },
  
  // Helper method to simulate progress (for demo purposes)
  simulateProgress: (id: string) => {
    let progress = 0;
    const interval = setInterval(() => {
      progress += Math.random() * 15;
      if (progress >= 100) {
        progress = 100;
        clearInterval(interval);
        get().updateTaskProgress(id, progress);
        get().updateTaskStatus(id, 'completed', `/results/${id}`);
        // Process next task in queue
        get().processNextTask();
      } else {
        get().updateTaskProgress(id, progress);
      }
    }, 1000);
  },
}));