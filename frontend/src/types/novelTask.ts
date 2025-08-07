export interface NovelTask {
  id: string;
  fileName: string;
  fileSize: number;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number; // 0-100
  uploadedAt: Date;
  startedAt?: Date;
  completedAt?: Date;
  resultUrl?: string;
  error?: string;
}