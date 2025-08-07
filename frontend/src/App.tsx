import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { FileUpload } from './components/FileUpload';
import { TaskList } from './components/TaskList';
import { TaskStats } from './components/TaskStats';
import { DatabaseManager } from './components/DatabaseManager';
import { ToastContainer } from './components/Toast';
import { ConnectionStatus } from './components/ConnectionStatus';
import { useWebSocket } from './hooks/useWebSocket';
import { useEffect } from 'react';
import { useTaskStore } from './store/novelTaskStore';
import { useToastStore } from './store/toastStore';
import { config } from './config';
import { Home, Database, Settings } from 'lucide-react';

function TaskManager() {
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

function Navigation() {
  const location = useLocation();

  const isActive = (path: string) => location.pathname === path;

  return (
    <nav className="bg-white shadow-sm border-b">
      <div className="px-6">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center space-x-8">
            <h1 className="text-xl font-bold text-gray-900">Novel Task Manager</h1>
            <div className="flex space-x-4">
              <Link
                to="/"
                className={`flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  isActive('/') 
                    ? 'bg-blue-100 text-blue-700' 
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                }`}
              >
                <Home className="w-4 h-4" />
                Tasks
              </Link>
              <Link
                to="/database"
                className={`flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  isActive('/database')
                    ? 'bg-blue-100 text-blue-700'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                }`}
              >
                <Database className="w-4 h-4" />
                Database
              </Link>
              <Link
                to="/settings"
                className={`flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  isActive('/settings')
                    ? 'bg-blue-100 text-blue-700'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                }`}
              >
                <Settings className="w-4 h-4" />
                Settings
              </Link>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <ConnectionStatus />
          </div>
        </div>
      </div>
    </nav>
  );
}

function SettingsPage() {
  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Settings</h2>
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-semibold mb-2">API Configuration</h3>
              <div className="space-y-2">
                <div className="flex items-center justify-between py-2">
                  <span className="text-gray-600">API URL</span>
                  <span className="font-mono text-sm">{config.API_URL}</span>
                </div>
                <div className="flex items-center justify-between py-2">
                  <span className="text-gray-600">WebSocket URL</span>
                  <span className="font-mono text-sm">{config.WS_URL}</span>
                </div>
                <div className="flex items-center justify-between py-2">
                  <span className="text-gray-600">Mock API</span>
                  <span className={`px-2 py-1 rounded text-xs font-medium ${
                    config.USE_MOCK_API ? 'bg-yellow-100 text-yellow-800' : 'bg-green-100 text-green-800'
                  }`}>
                    {config.USE_MOCK_API ? 'Enabled' : 'Disabled'}
                  </span>
                </div>
              </div>
            </div>
            
            <div>
              <h3 className="text-lg font-semibold mb-2">File Upload</h3>
              <div className="space-y-2">
                <div className="flex items-center justify-between py-2">
                  <span className="text-gray-600">Max File Size</span>
                  <span className="font-mono text-sm">{(config.MAX_FILE_SIZE / 1024 / 1024).toFixed(0)} MB</span>
                </div>
                <div className="flex items-center justify-between py-2">
                  <span className="text-gray-600">Allowed Extensions</span>
                  <span className="font-mono text-sm">{config.ALLOWED_EXTENSIONS.join(', ')}</span>
                </div>
              </div>
            </div>

            <div>
              <h3 className="text-lg font-semibold mb-2">Processing</h3>
              <div className="space-y-2">
                <div className="flex items-center justify-between py-2">
                  <span className="text-gray-600">Max Concurrent Tasks</span>
                  <span className="font-mono text-sm">{config.MAX_CONCURRENT_TASKS}</span>
                </div>
                <div className="flex items-center justify-between py-2">
                  <span className="text-gray-600">Task Timeout</span>
                  <span className="font-mono text-sm">30 minutes</span>
                </div>
              </div>
            </div>

            <div className="pt-4 border-t">
              <p className="text-sm text-gray-500">
                Note: These settings are read-only and configured on the server.
                Contact your administrator to modify these values.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function App() {
  const toasts = useToastStore((state) => state.toasts);
  const removeToast = useToastStore((state) => state.removeToast);

  return (
    <Router>
      <div className="h-screen flex flex-col">
        <Navigation />
        <div className="flex-1 overflow-hidden">
          <Routes>
            <Route path="/" element={<TaskManager />} />
            <Route path="/database" element={<DatabaseManager />} />
            <Route path="/settings" element={<SettingsPage />} />
          </Routes>
        </div>
        <ToastContainer toasts={toasts} onClose={removeToast} />
      </div>
    </Router>
  );
}

export default App;