import React, { useRef, useState } from 'react';
import { Upload, File, X, FolderOpen, FileText } from 'lucide-react';
import { useTaskStore } from '../store/novelTaskStore';
import { apiService } from '../services/api';
import { showSuccess, showInfo } from '../store/toastStore';

export const FileUpload: React.FC = () => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [dragActive, setDragActive] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const addTask = useTaskStore((state) => state.addTask);
  const tasks = useTaskStore((state) => state.tasks);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFiles(Array.from(e.dataTransfer.files));
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      handleFiles(Array.from(e.target.files));
    }
  };

  const handleFiles = (files: File[]) => {
    const textFiles = files.filter(file => 
      file.type === 'text/plain' || 
      file.name.endsWith('.txt') || 
      file.name.endsWith('.md')
    );
    setSelectedFiles(prev => [...prev, ...textFiles]);
  };

  const removeFile = (index: number) => {
    setSelectedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleUpload = async () => {
    if (isUploading) return;
    
    setIsUploading(true);
    const uploadingFiles = [...selectedFiles];
    setSelectedFiles([]);
    
    // 上传每个文件到后端
    for (const file of uploadingFiles) {
      try {
        // 调用后端上传接口
        const task = await apiService.uploadFile(file);
        
        // 添加任务到 store（使用后端返回的任务信息）
        addTask(file, task);
        
        showSuccess(`文件 ${file.name} 上传成功`);
      } catch (error) {
        console.error('Upload failed:', error);
        // 错误已经在 apiService 中处理并显示了
      }
    }
    
    setIsUploading(false);
  };

  const handleBatchUpload = async () => {
    if (isUploading) return;
    
    setIsUploading(true);
    showInfo('开始批量上传测试文件...');
    
    // Simulate batch upload of 10 files for testing
    for (let i = 1; i <= 10; i++) {
      const content = `这是测试小说 ${i} 的内容\n\n第一章\n\n这是一个测试文件，用于演示批量上传功能。`;
      const blob = new Blob([content], { type: 'text/plain' });
      const mockFile = new globalThis.File(
        [blob],
        `测试小说_${i}.txt`,
        { type: 'text/plain', lastModified: Date.now() }
      );
      
      try {
        // 上传到后端
        const task = await apiService.uploadFile(mockFile);
        addTask(mockFile, task);
      } catch (error) {
        console.error(`Failed to upload test file ${i}:`, error);
      }
    }
    
    showSuccess('批量上传完成！');
    setIsUploading(false);
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  const processingCount = tasks.filter(t => t.status === 'processing').length;
  const pendingCount = tasks.filter(t => t.status === 'pending').length;

  return (
    <div className="h-full flex flex-col p-4">
      <div className="mb-4">
        <h2 className="text-lg font-semibold text-gray-900 mb-2">文件上传</h2>
        <div className="text-xs text-gray-500 space-y-1">
          <p>支持格式: .txt, .md</p>
          <p>可批量上传多个文件</p>
        </div>
      </div>
      
      <div
        className={`relative ${
          dragActive ? 'bg-blue-50 border-blue-400' : 'bg-gray-50 border-gray-300'
        } border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-all hover:border-gray-400`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => !isUploading && fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".txt,.md,text/plain"
          className="hidden"
          onChange={handleChange}
          disabled={isUploading}
        />
        
        <Upload className={`mx-auto h-10 w-10 ${dragActive ? 'text-blue-500' : 'text-gray-400'} mb-3`} />
        <p className="text-sm font-medium text-gray-700">
          {isUploading ? '正在上传...' : dragActive ? '释放以上传文件' : '拖拽文件或点击选择'}
        </p>
        <p className="text-xs text-gray-500 mt-1">
          支持多文件批量上传
        </p>
      </div>

      {/* Quick Actions */}
      <div className="mt-4 space-y-2">
        <button
          onClick={() => fileInputRef.current?.click()}
          disabled={isUploading}
          className="w-full px-3 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 text-sm font-medium text-gray-700 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <FolderOpen className="w-4 h-4" />
          选择文件
        </button>
        
        <button
          onClick={handleBatchUpload}
          disabled={isUploading}
          className="w-full px-3 py-2 bg-gray-100 border border-gray-200 rounded-lg hover:bg-gray-200 text-sm text-gray-600 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <FileText className="w-4 h-4" />
          模拟批量上传 (10个文件)
        </button>
      </div>

      {/* Selected Files */}
      {selectedFiles.length > 0 && (
        <div className="mt-4 flex-1 flex flex-col">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-gray-700">
              待上传 ({selectedFiles.length} 个文件)
            </h3>
            <button
              onClick={() => setSelectedFiles([])}
              className="text-xs text-red-600 hover:text-red-700"
              disabled={isUploading}
            >
              清空全部
            </button>
          </div>
          
          <div className="flex-1 overflow-y-auto space-y-2 max-h-60">
            {selectedFiles.map((file, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-2 bg-white border border-gray-200 rounded-lg hover:border-gray-300"
              >
                <div className="flex items-center gap-2 flex-1 min-w-0">
                  <File className="w-4 h-4 text-gray-400 flex-shrink-0" />
                  <div className="min-w-0 flex-1">
                    <p className="text-sm text-gray-900 truncate" title={file.name}>
                      {file.name}
                    </p>
                    <p className="text-xs text-gray-500">{formatFileSize(file.size)}</p>
                  </div>
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    removeFile(index);
                  }}
                  disabled={isUploading}
                  className="p-1 hover:bg-gray-100 rounded flex-shrink-0 disabled:opacity-50"
                >
                  <X className="w-3 h-3 text-gray-500" />
                </button>
              </div>
            ))}
          </div>
          
          <button
            onClick={handleUpload}
            className="w-full mt-3 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium text-sm disabled:bg-gray-300 disabled:cursor-not-allowed"
            disabled={selectedFiles.length === 0 || isUploading}
          >
            {isUploading ? '正在上传...' : '开始处理'}
          </button>
        </div>
      )}

      {/* Queue Status */}
      {(processingCount > 0 || pendingCount > 0) && (
        <div className="mt-auto pt-4 border-t border-gray-200">
          <div className="space-y-2">
            {processingCount > 0 && (
              <div className="flex items-center justify-between text-sm">
                <span className="text-blue-600">正在处理:</span>
                <span className="font-semibold text-blue-700">{processingCount} 个任务</span>
              </div>
            )}
            {pendingCount > 0 && (
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600">队列等待:</span>
                <span className="font-semibold text-gray-700">{pendingCount} 个任务</span>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};