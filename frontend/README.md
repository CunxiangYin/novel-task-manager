# Novel Task Manager Frontend

React + TypeScript frontend application for the Novel Task Manager system.

最后更新: 2025年8月

## 📋 Features

- **File Upload Interface** - Drag & drop or click to upload multiple files
- **Real-time Task Processing** - Live progress updates via WebSocket
- **Task Management** - View, filter, sort, and manage processing tasks
- **Responsive Design** - Clean, modern UI with Tailwind CSS
- **Multi-task Support** - Handle multiple concurrent tasks efficiently

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ 
- npm or yarn
- Backend API running on http://localhost:8000

### Installation

```bash
# Install dependencies
npm install

# Copy environment configuration
cp .env.example .env

# Start development server
npm run dev
```

The application will be available at http://localhost:5174

### Build for Production

```bash
# Build production bundle
npm run build

# Preview production build
npm run preview
```

## 🏗️ Project Structure

```
frontend/
├── src/
│   ├── components/       # React components
│   │   ├── FileUpload.tsx
│   │   ├── TaskList.tsx
│   │   ├── TaskItem.tsx
│   │   └── TaskStats.tsx
│   ├── store/            # State management (Zustand)
│   │   └── novelTaskStore.ts
│   ├── types/            # TypeScript type definitions
│   │   └── novelTask.ts
│   ├── utils/            # Utility functions
│   ├── App.tsx          # Main application component
│   ├── main.tsx         # Application entry point
│   └── index.css        # Global styles
├── public/              # Static assets
├── dist/                # Production build output
└── package.json         # Dependencies and scripts
```

## 🎨 UI Components

### File Upload Panel (Left Sidebar)
- Drag & drop file upload
- Multiple file selection
- File type validation (.txt, .md)
- File size limit (10MB)
- Queue status display

### Task List (Main Area)
- Task progress bars with animations
- Status indicators (pending, processing, completed, failed)
- Filtering by status
- Sorting options (time, name, status)
- Batch operations (clear completed/failed)

### Task Statistics (Header)
- Real-time task counts
- Processing status overview
- Success/failure rates

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the frontend directory:

```env
VITE_API_URL=http://localhost:8000/api/v1
VITE_WS_URL=ws://localhost:8000/api/v1/ws
VITE_USE_MOCK_API=false
```

### Tailwind CSS

The project uses Tailwind CSS for styling. Configuration can be modified in `tailwind.config.js`.

## 📡 API Integration

The frontend communicates with the backend through:

1. **REST API** - File upload, task management
2. **WebSocket** - Real-time progress updates

### Key API Endpoints

- `POST /api/v1/tasks/upload` - Upload file
- `GET /api/v1/tasks` - List tasks
- `GET /api/v1/tasks/{id}` - Get task details
- `DELETE /api/v1/tasks/{id}` - Delete task
- `POST /api/v1/tasks/{id}/retry` - Retry failed task

## 🧪 Development

### Available Scripts

```bash
npm run dev      # Start development server
npm run build    # Build for production
npm run preview  # Preview production build
npm run lint     # Run ESLint
npm run type-check # TypeScript type checking
```

### State Management

The application uses Zustand for state management. The main store is located at `src/store/novelTaskStore.ts`.

### Mock Data

For development without backend, you can use the "模拟批量上传" button to generate test tasks.

## 🌏 Interface Language

The application currently uses Chinese labels with the following key terms:
- 文件上传 (File Upload)
- 任务列表 (Task List)
- 处理中 (Processing)
- 已完成 (Completed)
- 失败 (Failed)
- 等待中 (Pending)
- 查看详情 (View Details)
- 下载结果 (Download Result)

## 🚦 Task Processing Flow

1. User uploads file(s)
2. Task created with "pending" status
3. Backend processes file (max 3 concurrent)
4. Progress updates sent via WebSocket
5. Task marked as "completed" or "failed"
6. Result link available for completed tasks

## 🐛 Troubleshooting

### Common Issues

1. **Cannot connect to backend**
   - Ensure backend is running on port 8000
   - Check CORS settings in backend
   - Verify API URL in .env file

2. **WebSocket connection failed**
   - Check WS_URL in environment
   - Ensure backend WebSocket endpoint is active

3. **File upload fails**
   - Verify file type (.txt, .md only)
   - Check file size (<10MB)
   - Ensure backend upload directory exists

## 📦 Dependencies

### Core
- React 19.0.0
- TypeScript 5.6.2
- Vite 6.0.5

### UI
- Tailwind CSS 3.4.17
- Lucide React (icons)

### State & Utils
- Zustand 5.0.2 (state management)
- @dnd-kit/sortable (drag & drop)
- date-fns (date formatting)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆕 Recent Updates

- Upgraded to React 19 and Vite 6
- Added WebSocket auto-reconnection
- Improved task status handling
- Enhanced drag-and-drop support
- Added TypeScript strict mode
- Optimized bundle size

## 🔗 Related

- [Backend Documentation](../backend/README.md)
- [Database Design](../docs/database-design.md)
- [API Documentation](http://localhost:8000/docs)
- [Project Structure](../PROJECT_STRUCTURE.md)