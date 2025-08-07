import React, { useState, useEffect } from 'react';
import { 
  Database, 
  Trash2, 
  RefreshCw, 
  Download, 
  AlertCircle,
  CheckCircle,
  Server,
  HardDrive,
  FileText,
  Clock,
  BarChart3
} from 'lucide-react';
import { config } from '../config';

interface DatabaseStats {
  total_tasks: number;
  total_logs: number;
  total_results: number;
  total_queue_items: number;
  total_files: number;
  status_distribution: Record<string, number>;
  database_size_bytes: number;
  tasks_today: number;
}

interface TableInfo {
  name: string;
  row_count: number;
  columns: Array<{
    name: string;
    type: string;
    nullable: boolean;
    primary_key: boolean;
    foreign_key: boolean;
  }>;
}

interface QueryResult {
  table_name: string;
  total_count: number;
  count: number;
  offset: number;
  limit: number;
  data: Record<string, any>[];
}

export const DatabaseManager: React.FC = () => {
  const [stats, setStats] = useState<DatabaseStats | null>(null);
  const [tables, setTables] = useState<TableInfo[]>([]);
  const [selectedTable, setSelectedTable] = useState<string>('');
  const [tableData, setTableData] = useState<QueryResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error' | 'info'; text: string } | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'tables' | 'maintenance'>('overview');

  // Pagination
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 50;

  useEffect(() => {
    fetchStats();
    fetchTables();
  }, []);

  useEffect(() => {
    if (selectedTable) {
      fetchTableData(selectedTable, (currentPage - 1) * pageSize, pageSize);
    }
  }, [selectedTable, currentPage]);

  const fetchStats = async () => {
    try {
      const response = await fetch(`${config.API_URL}/database/stats`);
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (error) {
      console.error('Failed to fetch database stats:', error);
    }
  };

  const fetchTables = async () => {
    try {
      const response = await fetch(`${config.API_URL}/database/tables`);
      if (response.ok) {
        const data = await response.json();
        setTables(data);
      }
    } catch (error) {
      console.error('Failed to fetch tables info:', error);
    }
  };

  const fetchTableData = async (tableName: string, offset: number, limit: number) => {
    setLoading(true);
    try {
      const response = await fetch(
        `${config.API_URL}/database/query/${tableName}?offset=${offset}&limit=${limit}`
      );
      if (response.ok) {
        const data = await response.json();
        setTableData(data);
      }
    } catch (error) {
      console.error('Failed to fetch table data:', error);
      setMessage({ type: 'error', text: 'Failed to fetch table data' });
    } finally {
      setLoading(false);
    }
  };

  const handleCleanupLogs = async (days: number) => {
    if (!confirm(`Are you sure you want to delete logs older than ${days} days?`)) return;
    
    setLoading(true);
    try {
      const response = await fetch(
        `${config.API_URL}/database/cleanup/logs?days_old=${days}`,
        { method: 'DELETE' }
      );
      if (response.ok) {
        const result = await response.json();
        setMessage({ 
          type: 'success', 
          text: `Deleted ${result.deleted_count} old logs` 
        });
        fetchStats();
        fetchTables();
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to cleanup logs' });
    } finally {
      setLoading(false);
    }
  };

  const handleCleanupFailed = async (days: number) => {
    if (!confirm(`Are you sure you want to delete failed tasks older than ${days} days?`)) return;
    
    setLoading(true);
    try {
      const response = await fetch(
        `${config.API_URL}/database/cleanup/failed?days_old=${days}`,
        { method: 'DELETE' }
      );
      if (response.ok) {
        const result = await response.json();
        setMessage({ 
          type: 'success', 
          text: `Deleted ${result.deleted_count} failed tasks` 
        });
        fetchStats();
        fetchTables();
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to cleanup failed tasks' });
    } finally {
      setLoading(false);
    }
  };

  const handleVacuum = async () => {
    if (!confirm('Vacuum will optimize the database. This may take a moment. Continue?')) return;
    
    setLoading(true);
    try {
      const response = await fetch(`${config.API_URL}/database/vacuum`, { method: 'POST' });
      const result = await response.json();
      if (result.success) {
        setMessage({ type: 'success', text: result.message });
        fetchStats();
      } else {
        setMessage({ type: 'error', text: result.message });
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to vacuum database' });
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteTask = async (taskId: string) => {
    if (!confirm(`Are you sure you want to delete task ${taskId}?`)) return;
    
    setLoading(true);
    try {
      const response = await fetch(
        `${config.API_URL}/database/task/${taskId}`,
        { method: 'DELETE' }
      );
      if (response.ok) {
        setMessage({ type: 'success', text: `Task ${taskId} deleted` });
        if (selectedTable) {
          fetchTableData(selectedTable, (currentPage - 1) * pageSize, pageSize);
        }
        fetchStats();
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to delete task' });
    } finally {
      setLoading(false);
    }
  };

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  const totalPages = tableData ? Math.ceil(tableData.total_count / pageSize) : 0;

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Database className="w-8 h-8 text-blue-600" />
              <h1 className="text-2xl font-bold text-gray-900">Database Management</h1>
            </div>
            <button
              onClick={() => {
                fetchStats();
                fetchTables();
                setMessage({ type: 'info', text: 'Data refreshed' });
              }}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <RefreshCw className="w-4 h-4" />
              Refresh
            </button>
          </div>
        </div>

        {/* Alert Messages */}
        {message && (
          <div className={`mb-6 p-4 rounded-lg flex items-center gap-2 ${
            message.type === 'success' ? 'bg-green-50 text-green-800' :
            message.type === 'error' ? 'bg-red-50 text-red-800' :
            'bg-blue-50 text-blue-800'
          }`}>
            {message.type === 'success' ? <CheckCircle className="w-5 h-5" /> :
             message.type === 'error' ? <AlertCircle className="w-5 h-5" /> :
             <AlertCircle className="w-5 h-5" />}
            {message.text}
          </div>
        )}

        {/* Tabs */}
        <div className="bg-white rounded-lg shadow-sm mb-6">
          <div className="border-b border-gray-200">
            <nav className="flex space-x-8 px-6">
              {(['overview', 'tables', 'maintenance'] as const).map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`py-4 px-1 border-b-2 font-medium text-sm capitalize transition-colors ${
                    activeTab === tab
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700'
                  }`}
                >
                  {tab}
                </button>
              ))}
            </nav>
          </div>
        </div>

        {/* Overview Tab */}
        {activeTab === 'overview' && stats && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {/* Stats Cards */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Total Tasks</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.total_tasks}</p>
                </div>
                <FileText className="w-8 h-8 text-blue-500 opacity-50" />
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Database Size</p>
                  <p className="text-2xl font-bold text-gray-900">{formatBytes(stats.database_size_bytes)}</p>
                </div>
                <HardDrive className="w-8 h-8 text-green-500 opacity-50" />
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Tasks Today</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.tasks_today}</p>
                </div>
                <Clock className="w-8 h-8 text-purple-500 opacity-50" />
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Total Logs</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.total_logs}</p>
                </div>
                <Server className="w-8 h-8 text-orange-500 opacity-50" />
              </div>
            </div>

            {/* Status Distribution */}
            <div className="bg-white rounded-lg shadow-sm p-6 col-span-full">
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <BarChart3 className="w-5 h-5" />
                Task Status Distribution
              </h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {Object.entries(stats.status_distribution).map(([status, count]) => (
                  <div key={status} className="text-center">
                    <div className={`text-2xl font-bold ${
                      status === 'completed' ? 'text-green-600' :
                      status === 'failed' ? 'text-red-600' :
                      status === 'processing' ? 'text-blue-600' :
                      'text-gray-600'
                    }`}>
                      {count}
                    </div>
                    <div className="text-sm text-gray-600 capitalize">{status}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Tables Tab */}
        {activeTab === 'tables' && (
          <div className="space-y-6">
            {/* Table Selector */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h3 className="text-lg font-semibold mb-4">Select Table</h3>
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                {tables.map((table) => (
                  <button
                    key={table.name}
                    onClick={() => {
                      setSelectedTable(table.name);
                      setCurrentPage(1);
                    }}
                    className={`p-4 rounded-lg border-2 transition-colors ${
                      selectedTable === table.name
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <div className="font-medium">{table.name}</div>
                    <div className="text-sm text-gray-600">{table.row_count} rows</div>
                  </button>
                ))}
              </div>
            </div>

            {/* Table Data */}
            {selectedTable && tableData && (
              <div className="bg-white rounded-lg shadow-sm p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold">
                    {selectedTable} ({tableData.total_count} total rows)
                  </h3>
                  {totalPages > 1 && (
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                        disabled={currentPage === 1}
                        className="px-3 py-1 bg-gray-100 rounded hover:bg-gray-200 disabled:opacity-50"
                      >
                        Previous
                      </button>
                      <span className="text-sm text-gray-600">
                        Page {currentPage} of {totalPages}
                      </span>
                      <button
                        onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                        disabled={currentPage === totalPages}
                        className="px-3 py-1 bg-gray-100 rounded hover:bg-gray-200 disabled:opacity-50"
                      >
                        Next
                      </button>
                    </div>
                  )}
                </div>

                {loading ? (
                  <div className="text-center py-8">
                    <RefreshCw className="w-8 h-8 animate-spin mx-auto text-blue-600" />
                    <p className="mt-2 text-gray-600">Loading data...</p>
                  </div>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          {tableData.data.length > 0 &&
                            Object.keys(tableData.data[0]).map((key) => (
                              <th
                                key={key}
                                className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                              >
                                {key}
                              </th>
                            ))}
                          {selectedTable === 'tasks' && <th className="px-4 py-2"></th>}
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {tableData.data.map((row, idx) => (
                          <tr key={idx} className="hover:bg-gray-50">
                            {Object.entries(row).map(([key, value]) => (
                              <td key={key} className="px-4 py-2 text-sm text-gray-900 whitespace-nowrap">
                                {value === null ? (
                                  <span className="text-gray-400">null</span>
                                ) : typeof value === 'boolean' ? (
                                  value ? '✓' : '✗'
                                ) : (
                                  String(value).substring(0, 50)
                                )}
                              </td>
                            ))}
                            {selectedTable === 'tasks' && (
                              <td className="px-4 py-2">
                                <button
                                  onClick={() => handleDeleteTask(row.id)}
                                  className="text-red-600 hover:text-red-800"
                                  title="Delete task"
                                >
                                  <Trash2 className="w-4 h-4" />
                                </button>
                              </td>
                            )}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* Maintenance Tab */}
        {activeTab === 'maintenance' && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Cleanup Old Logs */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h3 className="text-lg font-semibold mb-4">Cleanup Old Logs</h3>
              <p className="text-sm text-gray-600 mb-4">
                Remove old task logs to free up space
              </p>
              <div className="space-y-2">
                <button
                  onClick={() => handleCleanupLogs(7)}
                  disabled={loading}
                  className="w-full px-4 py-2 bg-yellow-600 text-white rounded hover:bg-yellow-700 disabled:opacity-50"
                >
                  Delete logs older than 7 days
                </button>
                <button
                  onClick={() => handleCleanupLogs(30)}
                  disabled={loading}
                  className="w-full px-4 py-2 bg-orange-600 text-white rounded hover:bg-orange-700 disabled:opacity-50"
                >
                  Delete logs older than 30 days
                </button>
              </div>
            </div>

            {/* Cleanup Failed Tasks */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h3 className="text-lg font-semibold mb-4">Cleanup Failed Tasks</h3>
              <p className="text-sm text-gray-600 mb-4">
                Remove old failed tasks and associated files
              </p>
              <div className="space-y-2">
                <button
                  onClick={() => handleCleanupFailed(30)}
                  disabled={loading}
                  className="w-full px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 disabled:opacity-50"
                >
                  Delete failed tasks older than 30 days
                </button>
                <button
                  onClick={() => handleCleanupFailed(90)}
                  disabled={loading}
                  className="w-full px-4 py-2 bg-red-700 text-white rounded hover:bg-red-800 disabled:opacity-50"
                >
                  Delete failed tasks older than 90 days
                </button>
              </div>
            </div>

            {/* Database Optimization */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h3 className="text-lg font-semibold mb-4">Database Optimization</h3>
              <p className="text-sm text-gray-600 mb-4">
                Optimize database to reclaim unused space
              </p>
              <button
                onClick={handleVacuum}
                disabled={loading}
                className="w-full px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
              >
                Vacuum Database
              </button>
            </div>

            {/* Export Data */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h3 className="text-lg font-semibold mb-4">Export Data</h3>
              <p className="text-sm text-gray-600 mb-4">
                Export database tables to JSON format
              </p>
              <button
                onClick={() => {
                  setMessage({ type: 'info', text: 'Export feature coming soon!' });
                }}
                disabled={loading}
                className="w-full px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50 flex items-center justify-center gap-2"
              >
                <Download className="w-4 h-4" />
                Export All Data
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};