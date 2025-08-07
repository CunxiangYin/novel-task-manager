# CLAUDE.md - Frontend Source Code

## Overview
React TypeScript source code for the Novel Task Manager frontend application.

## Directory Structure
```
src/
├── components/          # UI Components
├── hooks/              # Custom React hooks
├── store/              # State management
├── config/             # Configuration
├── types/              # TypeScript definitions
├── utils/              # Helper functions
├── App.tsx            # Root component
├── main.tsx           # Entry point
└── index.css          # Global styles
```

## Component Guidelines

### Component Structure
```typescript
// FileUpload.tsx example structure
import React from 'react';
import { useTaskStore } from '../store/novelTaskStore';

interface FileUploadProps {
  // Props definition
}

export const FileUpload: React.FC<FileUploadProps> = (props) => {
  // Hooks
  const state = useTaskStore();
  
  // Local state
  const [files, setFiles] = useState([]);
  
  // Event handlers
  const handleUpload = () => {};
  
  // Effects
  useEffect(() => {}, []);
  
  // Render
  return <div>...</div>;
};
```

### Naming Conventions
- **Components**: PascalCase (TaskList, FileUpload)
- **Hooks**: camelCase with 'use' prefix (useWebSocket)
- **Utils**: camelCase (formatFileSize, calculateProgress)
- **Types**: PascalCase with suffix (TaskType, StatusEnum)
- **Constants**: UPPER_SNAKE_CASE (MAX_FILE_SIZE)

## State Management with Zustand

### Store Pattern
```typescript
interface TaskStore {
  // State
  tasks: Task[];
  
  // Actions
  addTask: (file: File) => void;
  updateTask: (id: string, updates: Partial<Task>) => void;
  removeTask: (id: string) => void;
  
  // Computed
  get pendingTasks() => Task[];
}
```

### Best Practices
1. Keep stores focused and small
2. Use immer for immutable updates
3. Separate actions from selectors
4. Use TypeScript for type safety

## Hook Patterns

### Custom Hook Template
```typescript
export const useCustomHook = (params) => {
  const [state, setState] = useState();
  
  useEffect(() => {
    // Setup
    return () => {
      // Cleanup
    };
  }, [dependencies]);
  
  const action = useCallback(() => {
    // Action logic
  }, [dependencies]);
  
  return { state, action };
};
```

### WebSocket Hook
- Auto-reconnection logic
- Message queue for offline
- Subscription management
- Connection status

## Type System

### Core Types
```typescript
interface Task {
  id: string;
  fileName: string;
  fileSize: number;
  status: TaskStatus;
  progress: number;
  uploadedAt: Date;
  resultUrl?: string;
  error?: string;
}

type TaskStatus = 'pending' | 'processing' | 'completed' | 'failed';
```

### Type Guards
```typescript
const isTask = (obj: any): obj is Task => {
  return obj && typeof obj.id === 'string';
};
```

## Styling with Tailwind

### Class Organization
```jsx
<div className={`
  // Layout
  flex flex-col
  // Spacing
  p-4 m-2
  // Sizing
  w-full h-64
  // Colors
  bg-white text-gray-900
  // Borders
  border border-gray-200 rounded-lg
  // Effects
  shadow-sm hover:shadow-md
  // Transitions
  transition-all duration-200
`}>
```

### Component Variants
```typescript
const variants = {
  primary: 'bg-blue-600 text-white',
  secondary: 'bg-gray-100 text-gray-900',
  danger: 'bg-red-600 text-white'
};
```

## Performance Optimization

### Memoization
```typescript
const MemoizedComponent = React.memo(Component, (prev, next) => {
  return prev.id === next.id;
});
```

### Code Splitting
```typescript
const LazyComponent = React.lazy(() => import('./Component'));
```

### Debouncing
```typescript
const debouncedSearch = useMemo(
  () => debounce(search, 300),
  [search]
);
```

## Error Handling

### Error Boundaries
```typescript
class ErrorBoundary extends React.Component {
  componentDidCatch(error, errorInfo) {
    console.error('Error caught:', error, errorInfo);
  }
}
```

### Try-Catch Patterns
```typescript
const uploadFile = async (file: File) => {
  try {
    const response = await api.upload(file);
    return response;
  } catch (error) {
    console.error('Upload failed:', error);
    showNotification('Upload failed');
  }
};
```

## Testing Approach

### Component Testing
```typescript
// TaskItem.test.tsx
describe('TaskItem', () => {
  it('should render task details', () => {
    const task = mockTask();
    render(<TaskItem task={task} />);
    expect(screen.getByText(task.fileName)).toBeInTheDocument();
  });
});
```

### Hook Testing
```typescript
// useWebSocket.test.ts
describe('useWebSocket', () => {
  it('should connect on mount', () => {
    const { result } = renderHook(() => useWebSocket());
    expect(result.current.isConnected).toBe(true);
  });
});
```

## Development Workflow

### Hot Module Replacement
- Vite provides instant updates
- State preserved during updates
- CSS changes apply immediately

### TypeScript Checking
```bash
# Check types without building
npx tsc --noEmit --watch

# Fix common issues
npx tsc --noEmit --listFiles
```

### Debugging
1. Use React DevTools
2. Enable source maps
3. Use console.log strategically
4. Check Network tab for API calls
5. Monitor WebSocket frames

## Common Patterns

### Loading States
```typescript
const [loading, setLoading] = useState(false);
const [error, setError] = useState(null);
const [data, setData] = useState(null);
```

### Form Handling
```typescript
const handleSubmit = (e: FormEvent) => {
  e.preventDefault();
  const formData = new FormData(e.target);
  // Process form
};
```

### Conditional Rendering
```jsx
{loading && <Spinner />}
{error && <Error message={error} />}
{data && <DataDisplay data={data} />}
```

## File Organization Best Practices
1. One component per file
2. Co-locate related files
3. Group by feature, not file type
4. Keep components small and focused
5. Extract reusable logic to hooks
6. Share types in central location