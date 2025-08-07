import React from 'react';
import { useTaskStore } from '../store/novelTaskStore';
import { Activity, CheckCircle, Clock, XCircle, Loader2 } from 'lucide-react';

export const TaskStats: React.FC = () => {
  const tasks = useTaskStore((state) => state.tasks);
  
  const stats = {
    total: tasks.length,
    pending: tasks.filter(t => t.status === 'pending').length,
    processing: tasks.filter(t => t.status === 'processing').length,
    completed: tasks.filter(t => t.status === 'completed').length,
    failed: tasks.filter(t => t.status === 'failed').length,
  };

  return (
    <div className="flex items-center gap-6">
      <div className="flex items-center gap-2">
        <Activity className="w-4 h-4 text-gray-500" />
        <span className="text-sm text-gray-600">总任务:</span>
        <span className="text-sm font-semibold text-gray-900">{stats.total}</span>
      </div>
      
      {stats.pending > 0 && (
        <div className="flex items-center gap-2">
          <Clock className="w-4 h-4 text-gray-400" />
          <span className="text-sm text-gray-600">等待:</span>
          <span className="text-sm font-semibold text-gray-700">{stats.pending}</span>
        </div>
      )}
      
      {stats.processing > 0 && (
        <div className="flex items-center gap-2">
          <Loader2 className="w-4 h-4 text-blue-500 animate-spin" />
          <span className="text-sm text-blue-600">处理中:</span>
          <span className="text-sm font-semibold text-blue-700">{stats.processing}</span>
        </div>
      )}
      
      {stats.completed > 0 && (
        <div className="flex items-center gap-2">
          <CheckCircle className="w-4 h-4 text-green-500" />
          <span className="text-sm text-green-600">完成:</span>
          <span className="text-sm font-semibold text-green-700">{stats.completed}</span>
        </div>
      )}
      
      {stats.failed > 0 && (
        <div className="flex items-center gap-2">
          <XCircle className="w-4 h-4 text-red-500" />
          <span className="text-sm text-red-600">失败:</span>
          <span className="text-sm font-semibold text-red-700">{stats.failed}</span>
        </div>
      )}
    </div>
  );
};