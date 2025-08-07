import React, { useState } from 'react';
import { useTaskStore } from '../store/novelTaskStore';
import { TaskItem } from './TaskItem';
import { Filter, SortAsc, Trash2, CheckCircle, XCircle } from 'lucide-react';

type FilterStatus = 'all' | 'pending' | 'processing' | 'completed' | 'failed';
type SortBy = 'time' | 'name' | 'status';

export const TaskList: React.FC = () => {
  const tasks = useTaskStore((state) => state.tasks);
  const removeTask = useTaskStore((state) => state.removeTask);
  const [filterStatus, setFilterStatus] = useState<FilterStatus>('all');
  const [sortBy, setSortBy] = useState<SortBy>('time');

  // Filter tasks
  const filteredTasks = tasks.filter(task => {
    if (filterStatus === 'all') return true;
    return task.status === filterStatus;
  });

  // Sort tasks
  const sortedTasks = [...filteredTasks].sort((a, b) => {
    switch (sortBy) {
      case 'name':
        return a.fileName.localeCompare(b.fileName);
      case 'status':
        const statusOrder = { pending: 0, processing: 1, completed: 2, failed: 3 };
        return statusOrder[a.status] - statusOrder[b.status];
      case 'time':
      default:
        return b.uploadedAt.getTime() - a.uploadedAt.getTime();
    }
  });

  const clearCompleted = () => {
    tasks
      .filter(task => task.status === 'completed')
      .forEach(task => removeTask(task.id));
  };

  const clearFailed = () => {
    tasks
      .filter(task => task.status === 'failed')
      .forEach(task => removeTask(task.id));
  };

  const clearAll = () => {
    if (window.confirm('确定要清空所有任务吗？')) {
      tasks.forEach(task => removeTask(task.id));
    }
  };

  if (tasks.length === 0) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center">
          <svg
            className="mx-auto h-12 w-12 text-gray-400"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
          <h3 className="mt-2 text-sm font-medium text-gray-900">暂无任务</h3>
          <p className="mt-1 text-sm text-gray-500">
            请在左侧上传文件开始处理
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col">
      {/* Toolbar */}
      <div className="flex-shrink-0 bg-white border-b border-gray-200 px-6 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            {/* Filter */}
            <div className="flex items-center gap-2">
              <Filter className="w-4 h-4 text-gray-400" />
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value as FilterStatus)}
                className="text-sm border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="all">全部任务 ({tasks.length})</option>
                <option value="pending">等待中 ({tasks.filter(t => t.status === 'pending').length})</option>
                <option value="processing">处理中 ({tasks.filter(t => t.status === 'processing').length})</option>
                <option value="completed">已完成 ({tasks.filter(t => t.status === 'completed').length})</option>
                <option value="failed">失败 ({tasks.filter(t => t.status === 'failed').length})</option>
              </select>
            </div>

            {/* Sort */}
            <div className="flex items-center gap-2">
              <SortAsc className="w-4 h-4 text-gray-400" />
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as SortBy)}
                className="text-sm border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="time">按时间排序</option>
                <option value="name">按名称排序</option>
                <option value="status">按状态排序</option>
              </select>
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center gap-2">
            {tasks.filter(t => t.status === 'completed').length > 0 && (
              <button
                onClick={clearCompleted}
                className="px-3 py-1.5 text-sm text-green-600 hover:text-green-700 hover:bg-green-50 rounded-md flex items-center gap-1"
              >
                <CheckCircle className="w-4 h-4" />
                清除已完成
              </button>
            )}
            {tasks.filter(t => t.status === 'failed').length > 0 && (
              <button
                onClick={clearFailed}
                className="px-3 py-1.5 text-sm text-red-600 hover:text-red-700 hover:bg-red-50 rounded-md flex items-center gap-1"
              >
                <XCircle className="w-4 h-4" />
                清除失败
              </button>
            )}
            {tasks.length > 0 && (
              <button
                onClick={clearAll}
                className="px-3 py-1.5 text-sm text-gray-600 hover:text-gray-700 hover:bg-gray-50 rounded-md flex items-center gap-1"
              >
                <Trash2 className="w-4 h-4" />
                清空全部
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Task List */}
      <div className="flex-1 overflow-y-auto bg-gray-50 p-6">
        <div className="space-y-3">
          {sortedTasks.map((task, index) => (
            <TaskItem key={task.id} task={task} index={index + 1} />
          ))}
        </div>

        {/* Load More Indicator */}
        {sortedTasks.length >= 20 && (
          <div className="mt-6 text-center">
            <p className="text-sm text-gray-500">
              显示 {sortedTasks.length} 个任务
            </p>
          </div>
        )}
      </div>
    </div>
  );
};