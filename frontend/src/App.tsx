import { FileUpload } from './components/FileUpload';
import { TaskList } from './components/TaskList';
import { TaskStats } from './components/TaskStats';
import { useWebSocket } from './hooks/useWebSocket';
import { useEffect } from 'react';
import { useTaskStore } from './store/novelTaskStore';
import { config } from './config';

function App() {
  const { subscribeToTask } = useWebSocket();
  const tasks = useTaskStore((state) => state.tasks);

  // Subscribe to all active tasks
  useEffect(() => {
    if (!config.USE_MOCK_API) {
      tasks
        .filter(task => task.status === 'processing' || task.status === 'pending')
        .forEach(task => {
          subscribeToTask(task.id);
        });
    }
  }, [tasks, subscribeToTask]);

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b flex-shrink-0">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold text-gray-900">小说处理任务管理器</h1>
            <TaskStats />
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 overflow-hidden">
        <div className="h-full flex">
          {/* Left Sidebar - File Upload */}
          <aside className="w-80 bg-white border-r border-gray-200 flex flex-col">
            <FileUpload />
          </aside>

          {/* Right Content - Task List */}
          <section className="flex-1 overflow-hidden">
            <TaskList />
          </section>
        </div>
      </main>
    </div>
  );
}

export default App;