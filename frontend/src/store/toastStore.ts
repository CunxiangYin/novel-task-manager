import { create } from 'zustand';
import { ToastType } from '../components/Toast';

interface Toast {
  id: string;
  type: ToastType;
  title: string;
  message?: string;
  duration?: number;
}

interface ToastStore {
  toasts: Toast[];
  addToast: (toast: Omit<Toast, 'id'>) => void;
  removeToast: (id: string) => void;
  clearToasts: () => void;
}

export const useToastStore = create<ToastStore>((set) => ({
  toasts: [],
  
  addToast: (toast) => {
    const id = `toast-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    set((state) => ({
      toasts: [...state.toasts, { ...toast, id }],
    }));
  },
  
  removeToast: (id) => {
    set((state) => ({
      toasts: state.toasts.filter((toast) => toast.id !== id),
    }));
  },
  
  clearToasts: () => {
    set({ toasts: [] });
  },
}));

// Helper functions for common toast types
export const showSuccess = (title: string, message?: string) => {
  useToastStore.getState().addToast({
    type: 'success',
    title,
    message,
    duration: 3000,
  });
};

export const showError = (title: string, message?: string) => {
  useToastStore.getState().addToast({
    type: 'error',
    title,
    message,
    duration: 6000,
  });
};

export const showWarning = (title: string, message?: string) => {
  useToastStore.getState().addToast({
    type: 'warning',
    title,
    message,
    duration: 5000,
  });
};

export const showInfo = (title: string, message?: string) => {
  useToastStore.getState().addToast({
    type: 'info',
    title,
    message,
    duration: 4000,
  });
};

export const showNetworkError = () => {
  useToastStore.getState().addToast({
    type: 'network',
    title: '网络连接失败',
    message: '无法连接到服务器，请检查网络连接或稍后重试',
    duration: 0, // Don't auto-dismiss network errors
  });
};