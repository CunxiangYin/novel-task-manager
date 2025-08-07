# CLAUDE.md - Frontend Application

## Overview
React 19 frontend for the Novel Task Manager application with TypeScript, Vite, and Tailwind CSS.

## Tech Stack
- **Framework**: React 19.0.0
- **Language**: TypeScript 5.6.2
- **Build Tool**: Vite 6.0.5
- **Styling**: Tailwind CSS 3.4.17
- **State Management**: Zustand 5.0.2
- **Drag & Drop**: @dnd-kit/sortable
- **Icons**: Lucide React
- **Date Handling**: date-fns

## Project Structure
```
frontend/
├── src/
│   ├── components/        # React components
│   │   ├── FileUpload.tsx    # File upload interface
│   │   ├── TaskList.tsx      # Task list display
│   │   ├── TaskItem.tsx      # Individual task card
│   │   └── TaskStats.tsx     # Statistics display
│   ├── hooks/            # Custom React hooks
│   │   └── useWebSocket.ts   # WebSocket connection management
│   ├── store/            # State management
│   │   └── novelTaskStore.ts # Zustand store for tasks
│   ├── config/           # Configuration
│   │   └── index.ts          # App configuration
│   ├── types/            # TypeScript types
│   │   └── index.ts          # Type definitions
│   ├── utils/            # Utility functions
│   │   └── format.ts         # Formatting helpers
│   ├── App.tsx           # Main application component
│   └── main.tsx          # Application entry point
├── public/               # Static assets
└── index.html           # HTML template
```

## Component Architecture

### FileUpload Component
- Drag-and-drop file upload interface
- File validation (type and size)
- Batch upload support
- Queue status display

### TaskList Component
- Displays all tasks in a scrollable list
- Groups tasks by status
- Real-time progress updates
- Drag-to-reorder support

### TaskItem Component
- Individual task card with progress bar
- Status indicators and animations
- Result download links
- Error message display

### TaskStats Component
- Overall statistics display
- Real-time metrics updates
- Success rate calculation

## State Management

### Zustand Store Structure
```typescript
interface TaskStore {
  tasks: Task[]
  addTask: (file: File) => void
  updateTaskStatus: (id, status, resultUrl?, error?) => void
  updateTaskProgress: (id, progress) => void
  removeTask: (id) => void
  reorderTasks: (tasks) => void
  processNextTask: () => void
}
```

## WebSocket Integration
- Auto-reconnection with 3-second delay
- Task subscription management
- Real-time progress updates
- Connection status monitoring

## Configuration
```typescript
// src/config/index.ts
export const config = {
  API_URL: 'http://localhost:8000/api/v1',
  WS_URL: 'ws://localhost:8000/api/v1/ws',
  USE_MOCK_API: false,
  MAX_FILE_SIZE: 10485760, // 10MB
  ALLOWED_EXTENSIONS: ['.txt', '.md']
}
```

## Development Commands
```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run preview      # Preview production build
npm run type-check   # Run TypeScript compiler
```

## Styling Guidelines
- Uses Tailwind CSS utility classes
- Color scheme: Blue primary, gray secondary
- Responsive design with mobile-first approach
- Smooth animations and transitions

## Performance Optimizations
1. **React.memo** for expensive components
2. **useCallback** for event handlers
3. **Virtualization** ready for large task lists
4. **Debounced** WebSocket reconnection
5. **Optimistic UI** updates

## Testing
```bash
# Type checking
npx tsc --noEmit

# Build validation
npm run build

# Development with hot reload
npm run dev
```

## Common Issues & Solutions

### WebSocket Connection Issues
- Check CORS settings in backend
- Verify WS_URL in config
- Check browser console for errors

### Build Errors
- Run `npm run type-check` to identify issues
- Clear node_modules and reinstall
- Check for missing dependencies

### Performance Issues
- Enable React DevTools Profiler
- Check for unnecessary re-renders
- Consider implementing virtualization for large lists

## Future Enhancements
1. Add task filtering and search
2. Implement task priority management
3. Add dark mode support
4. Enhanced error handling and retry logic
5. Progress persistence across sessions
6. Export task history
7. Multi-language support