import React from 'react';
import { NovelTask } from '../types/novelTask';
import { CheckCircle, XCircle, Clock, Loader2, FileText, ExternalLink, Trash2, RotateCw } from 'lucide-react';
import { useTaskStore } from '../store/novelTaskStore';

interface TaskItemProps {
  task: NovelTask;
  index: number;
}

export const TaskItem: React.FC<TaskItemProps> = ({ task, index }) => {
  const removeTask = useTaskStore((state) => state.removeTask);
  const updateTaskStatus = useTaskStore((state) => state.updateTaskStatus);

  const getStatusIcon = () => {
    switch (task.status) {
      case 'pending':
        return <Clock className="w-5 h-5 text-gray-400" />;
      case 'processing':
        return <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />;
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'failed':
        return <XCircle className="w-5 h-5 text-red-500" />;
    }
  };

  const getStatusText = () => {
    switch (task.status) {
      case 'pending':
        return '等待中';
      case 'processing':
        return '处理中';
      case 'completed':
        return '已完成';
      case 'failed':
        return '失败';
    }
  };

  const getStatusColor = () => {
    switch (task.status) {
      case 'pending':
        return 'bg-gray-50 border-gray-200';
      case 'processing':
        return 'bg-blue-50 border-blue-200';
      case 'completed':
        return 'bg-green-50 border-green-200';
      case 'failed':
        return 'bg-red-50 border-red-200';
    }
  };

  const getProgressBarColor = () => {
    switch (task.status) {
      case 'pending':
        return 'bg-gray-300';
      case 'processing':
        return 'bg-blue-500';
      case 'completed':
        return 'bg-green-500';
      case 'failed':
        return 'bg-red-500';
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  const formatTime = (date: Date) => {
    return new Date(date).toLocaleTimeString('zh-CN', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  };

  const handleRetry = () => {
    updateTaskStatus(task.id, 'pending');
    // Simulate retry
    setTimeout(() => {
      updateTaskStatus(task.id, 'processing');
      const store = useTaskStore.getState();
      store.simulateProgress(task.id);
    }, 1000);
  };

  return (
    <div className={`rounded-lg border p-4 transition-all hover:shadow-md ${getStatusColor()}`}>
      <div className="flex items-center gap-4">
        {/* Task Number */}
        <div className="flex-shrink-0">
          <div className="flex items-center justify-center w-10 h-10 bg-white rounded-lg border border-gray-300 font-semibold text-sm">
            {index}
          </div>
        </div>

        {/* File Info */}
        <div className="flex-shrink-0 w-48">
          <div className="flex items-center gap-2">
            <FileText className="w-4 h-4 text-gray-400" />
            <div className="min-w-0 flex-1">
              <p className="text-sm font-medium text-gray-900 truncate" title={task.fileName}>
                {task.fileName}
              </p>
              <p className="text-xs text-gray-500">
                {formatFileSize(task.fileSize)} • {formatTime(task.uploadedAt)}
              </p>
            </div>
          </div>
        </div>

        {/* Task Label */}
        <div className="flex-shrink-0 w-24">
          <div className="bg-white px-3 py-1 rounded-md border border-gray-300">
            <p className="text-sm font-mono text-gray-700">task.{index}</p>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="flex-1 min-w-0">
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                {getStatusIcon()}
                <span className="text-sm font-medium text-gray-700">
                  {getStatusText()}
                </span>
              </div>
              <span className="text-sm font-medium text-gray-600">{Math.round(task.progress)}%</span>
            </div>
            <div className="relative">
              <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
                <div
                  className={`h-full transition-all duration-500 ease-out ${getProgressBarColor()}`}
                  style={{ width: `${task.progress}%` }}
                />
              </div>
              {task.status === 'processing' && (
                <div className="absolute inset-0 rounded-full overflow-hidden">
                  <div className="h-full bg-gradient-to-r from-transparent via-white/30 to-transparent animate-shimmer" />
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Result Link */}
        <div className="flex-shrink-0 w-32">
          {task.status === 'completed' && task.resultUrl ? (
            <a
              href={task.resultUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors text-sm font-medium w-full justify-center"
            >
              查看详情
              <ExternalLink className="w-3.5 h-3.5" />
            </a>
          ) : task.status === 'failed' ? (
            <button
              onClick={handleRetry}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-red-100 text-red-600 rounded-md hover:bg-red-200 transition-colors text-sm font-medium w-full justify-center"
            >
              重试
              <RotateCw className="w-3.5 h-3.5" />
            </button>
          ) : (
            <div className="inline-flex items-center px-3 py-1.5 bg-gray-100 text-gray-400 rounded-md text-sm w-full justify-center">
              待生成
            </div>
          )}
        </div>

        {/* Actions */}
        <div className="flex-shrink-0">
          <button
            onClick={() => removeTask(task.id)}
            className="p-1.5 text-gray-400 hover:text-red-500 hover:bg-white rounded-md transition-colors"
            title="删除任务"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Error Message */}
      {task.status === 'failed' && task.error && (
        <div className="mt-3 p-2 bg-red-100 border border-red-300 rounded-md">
          <p className="text-xs text-red-700">
            {task.error.includes('timeout') || task.error.includes('exceeded') ? (
              <>
                ⏱️ {task.error}
                <span className="block mt-1 text-red-600">
                  任务处理时间超过了允许的最大时长（30分钟）
                </span>
              </>
            ) : (
              task.error
            )}
          </p>
        </div>
      )}

      {/* Processing Details */}
      {task.status === 'processing' && (
        <div className="mt-3 flex items-center gap-4 text-xs text-gray-500">
          <span>开始时间: {task.startedAt ? formatTime(task.startedAt) : '-'}</span>
          <span>
            {(() => {
              // Calculate elapsed time and estimate remaining
              if (task.startedAt && task.progress > 0) {
                const elapsedMs = new Date().getTime() - new Date(task.startedAt).getTime();
                const elapsedMinutes = Math.floor(elapsedMs / 60000);
                const estimatedTotalMinutes = (elapsedMinutes / task.progress) * 100;
                const remainingMinutes = Math.ceil(estimatedTotalMinutes - elapsedMinutes);
                
                if (remainingMinutes > 60) {
                  const hours = Math.floor(remainingMinutes / 60);
                  const mins = remainingMinutes % 60;
                  return `预计剩余: ${hours}小时${mins}分钟`;
                } else if (remainingMinutes > 0) {
                  return `预计剩余: ${remainingMinutes}分钟`;
                } else {
                  return '即将完成...';
                }
              }
              return '计算中...';
            })()}
          </span>
          <span className="text-orange-600">
            {task.startedAt && (() => {
              const elapsedMs = new Date().getTime() - new Date(task.startedAt).getTime();
              const elapsedMinutes = Math.floor(elapsedMs / 60000);
              if (elapsedMinutes > 25) {
                return '⚠️ 接近超时限制(30分钟)';
              }
              return '';
            })()}
          </span>
        </div>
      )}
    </div>
  );
};