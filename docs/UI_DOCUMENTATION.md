# UI (Frontend) Documentation

## Table of Contents
1. [Overview](#overview)
2. [Tech Stack](#tech-stack)
3. [Backend API Reference](#backend-api-reference)
4. [UI Requirements](#ui-requirements)
5. [UI Components](#ui-components)
6. [State Management](#state-management)
7. [Project Structure](#project-structure)
8. [Environment Variables](#environment-variables)

---

## Overview

The UI replicates the functionality of the Backend Swagger UI, providing a web interface for:
- File upload (circuit `.py` or `.spice` files)
- Running simulations
- Running optimization/parameter synthesis
- Checking job status
- Download results (ZIP with netlists, plots, metrics)
- Introspecting circuit parameters

---

## Tech Stack

| Category | Technology |
|----------|------------|
| Framework | React (Vite) |
| Package Manager | pnpm |
| Language | TypeScript |
| HTTP Client | Axios |
| Routing | react-router-dom |
| Styling | CSS Modules / Plain CSS |

**Current Dependencies** (`frontend/package.json`):
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "axios": "^1.6.2"
  }
}
```

---

## Backend API Reference

**Base URL:** `http://localhost:8000` (configurable via `VITE_API_BASE_URL`)

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/api/v1/run` | Upload circuit file, run simulation/optimization |
| `GET` | `/api/v1/status/{process_id}` | Get job status and results |
| `GET` | `/api/v1/download/{process_id}` | Download ZIP with results |
| `POST` | `/api/v1/introspect` | Extract default parameters from circuit file |

---

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "ok"
}
```

---

### POST /api/v1/run

Upload circuit file and run simulation or optimization.

**Content-Type:** `multipart/form-data`

**Form Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `file` | File | Yes | Circuit `.py` or `.spice` file |
| `parameters` | JSON string | No | Circuit parameters as JSON string |
| `mode` | string | No | `"simulate"` (default) or `"optimize"` |

**Response:**
```json
{
  "process_id": "proc_abc123def456",
  "filename": "circuit.py",
  "status": "RUNNING",
  "parameters": {},
  "mode": "simulate",
  "message": "Circuit processing started."
}
```

**Status Values:** `PENDING`, `RUNNING`, `COMPLETED`, `FAILED`

---

### GET /api/v1/status/{process_id}

Check job status and retrieve results.

**Path Parameters:**
- `process_id` - The ID returned from `/run`

**Response (Simulate Mode):**
```json
{
  "process_id": "proc_abc123def456",
  "filename": "circuit.py",
  "status": "COMPLETED",
  "progress": 100,
  "parameters": {},
  "mode": "simulate",
  "results": {
    "netlists": {...},
    "metrics": {...},
    "plots": [...]
  },
  "error": null,
  "created_at": "2026-04-20T10:00:00",
  "updated_at": "2026-04-20T10:05:00"
}
```

**Response (Optimize Mode):**
```json
{
  "process_id": "proc_abc123def456",
  "filename": "circuit.py",
  "status": "COMPLETED",
  "progress": 100,
  "parameters": {},
  "mode": "optimize",
  "results": {
    "job_id": "proc_abc123def456",
    "mode": "optimize",
    "status": "COMPLETED",
    "epochs": [...],
    "best": {
      "parameters": {"w": 10.5, "l": 0.18},
      "metrics": {...},
      "cost": 0.123
    },
    "summary": {
      "iterations": 100,
      "errors": []
    }
  },
  "error": null,
  "created_at": "2026-04-20T10:00:00",
  "updated_at": "2026-04-20T10:05:00"
}
```

---

### GET /api/v1/download/{process_id}

Download ZIP file containing results.

**Simulate Mode:** Returns ZIP containing:
- SPICE netlists (`.spice`)
- Plot images (`.png`)
- Summary JSON (`summary_*.json`)
- Source file (`source_*.py`)

**Optimize Mode:** Returns JSON with optimization results.

---

### POST /api/v1/introspect

Extract default parameters from a circuit `.py` file.

**Content-Type:** `multipart/form-data`

**Form Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `file` | File | Yes | Circuit `.py` file |

**Response:**
```json
{
  "parameters": [
    {
      "name": "w",
      "type": "float",
      "default": 1.0,
      "description": "Width parameter"
    }
  ]
}
```

---

## UI Requirements

### 1. Home Page

- Hero section with project introduction
- Feature highlights
- Navigation to Dashboard

### 2. Dashboard Page

**2.1 Upload Section**
- File dropzone/selector for circuit files
- Supported file types: `.py`, `.spice`
- File validation and preview

**2.2 Parameters Section**
- JSON editor for circuit parameters
- Default values from introspection
- Parameter validation
- Mode toggle: Simulate / Optimize

**2.3 Job Control**
- Run button to submit job
- Cancel button (optional)

**2.4 Status Section**
- Current job status display
- Progress indicator (for RUNNING status)
- Poll for status updates

**2.5 Results Section**
- Results display (metrics, plots)
- Download button for ZIP results

### 3. Backend Status Indicator

- Always-visible backend connection status
- Auto-reconnect on failure

---

## UI Components

### Required Components

```
src/
├── components/
│   ├── FileUploader.tsx       # File upload with drag-and-drop
│   ├── ParameterEditor.tsx   # JSON parameter input
│   ├── ModeToggle.tsx        # Simulate/Optimize toggle
│   ├── JobStatus.tsx         # Status display with progress
│   ├── ResultsViewer.tsx     # Results visualization
│   ├── PlotViewer.tsx        # Image viewer for plots
│   ├── MetricsTable.tsx      # Metrics display table
│   ├── DownloadButton.tsx   # Download ZIP button
│   ├── BackendStatus.tsx     # Backend connection indicator
│   └── Navbar.tsx            # Navigation
├── pages/
│   ├── HomePage.tsx          # Landing page
│   └── DashboardPage.tsx     # Main application page
├── services/
│   └── api.ts                # API client (upgrade needed)
├── hooks/
│   ├── useApi.ts            # Generic API hook
│   ├── useBackendHealth.ts   # Health check hook
│   └── usePolling.ts         # Status polling hook
└── App.tsx                   # Router setup
```

### Component Specifications

#### FileUploader

```typescript
interface FileUploaderProps {
  onFileSelect: (file: File) => void;
  accept: string;           // ".py,.spice"
  maxSize?: number;         // bytes
}
```

#### ParameterEditor

```typescript
interface ParameterEditorProps {
  parameters: Record<string, unknown>;
  onChange: (params: Record<string, unknown>) => void;
  readOnly?: boolean;
}
```

#### JobStatus

```typescript
interface JobStatusProps {
  status: ProcessStatus;
  progress: number;
  error?: string | null;
  results?: unknown;
}

type ProcessStatus = 'PENDING' | 'RUNNING' | 'COMPLETED' | 'FAILED';
```

#### PlotViewer

```typescript
interface PlotViewerProps {
  plots: string[];  // URLs or base64 strings
}
```

---

## State Management

### Local State (useState)

For simple components:
- File selection
- Parameter values
- UI toggles

### Custom Hooks

```typescript
// usePolling.ts - Poll endpoint at intervals
function usePolling<T>(
  fetchFn: () => Promise<T>,
  interval: number,
  shouldPoll: boolean
): {
  data: T | null;
  loading: boolean;
  error: string | null;
  start: () => void;
  stop: () => void;
}
```

```typescript
// useJob.ts - Full job lifecycle
function useJob() {
  // Submit job
  const submitJob: (file: File, params: object, mode: string) => Promise<string>;
  
  // Check status
  const status: ProcessStatus;
  const progress: number;
  const results: object | null;
  
  // Actions
  const downloadResults: () => Promise<Blob>;
}
```

---

## Project Structure

```
frontend/
├── public/
├── src/
│   ├── components/
│   │   ├── BackendStatus.tsx
│   │   ├── FeatureCard.tsx
│   │   ├── FeaturesSection.tsx
│   │   ├── HeroSection.tsx
│   │   ├── Navbar.tsx
│   │   ├── FileUploader.tsx      # NEW
│   │   ├── ParameterEditor.tsx   # NEW
│   │   ├── ModeToggle.tsx        # NEW
│   │   ├── JobStatus.tsx         # NEW
│   │   ├── ResultsViewer.tsx     # NEW
│   │   └── PlotViewer.tsx        # NEW
│   ├── pages/
│   │   ├── HomePage.tsx
│   │   └── DashboardPage.tsx     # UPDATE
│   ├── services/
│   │   └── api.ts               # UPGRADE
│   ├── hooks/
│   │   ├── useApi.ts
│   │   ├── useBackendHealth.ts
│   │   ├── useJob.ts             # NEW
│   │   └── usePolling.ts        # NEW
│   ├── types/
│   │   └── api.ts               # NEW - TypeScript interfaces
│   ├── utils/
│   │   └── health.ts
│   ├── layouts/
│   │   ├── AppLayout.tsx
│   │   └── MainLayout.tsx
│   ├── App.tsx
│   ├── main.tsx
│   └── vite-env.d.ts
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
└── .env.example
```

---

## Environment Variables

Create `frontend/.env`:

```env
VITE_API_BASE_URL=http://localhost:8000
```

---

## API Service Upgrade

The current `services/api.ts` needs to be upgraded to support all endpoints:

```typescript
// src/services/api.ts

import axios, { AxiosInstance } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export interface ProcessStatusResponse {
  process_id: string;
  filename: string;
  status: 'PENDING' | 'RUNNING' | 'COMPLETED' | 'FAILED';
  progress: number;
  parameters: Record<string, unknown>;
  mode: string;
  results: Record<string, unknown> | null;
  error: string | null;
  created_at: string;
  updated_at: string;
}

export interface RunResponse {
  process_id: string;
  filename: string;
  status: string;
  parameters: Record<string, unknown>;
  mode: string;
  message: string;
}

export interface ParameterSpec {
  name: string;
  type: string;
  default: unknown;
  description: string;
}

export interface IntrospectResponse {
  parameters: ParameterSpec[];
}

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
    });
  }

  async getHealth(): Promise<{ status: string }> {
    const response = await this.client.get('/health');
    return response.data;
  }

  async runCircuit(
    file: File,
    parameters: Record<string, unknown> = {},
    mode: string = 'simulate'
  ): Promise<RunResponse> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('parameters', JSON.stringify(parameters));
    formData.append('mode', mode);

    const response = await this.client.post('/api/v1/run', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  }

  async getStatus(processId: string): Promise<ProcessStatusResponse> {
    const response = await this.client.get(`/api/v1/status/${processId}`);
    return response.data;
  }

  async downloadResults(processId: string): Promise<Blob> {
    const response = await this.client.get(`/api/v1/download/${processId}`, {
      responseType: 'blob',
    });
    return response.data;
  }

  async introspect(file: File): Promise<IntrospectResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await this.client.post('/api/v1/introspect', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  }
}

export default new ApiClient();
```

---

## Implementation Checklist

### Phase 1: Core Infrastructure
- [ ] Create TypeScript types (`src/types/api.ts`)
- [ ] Upgrade API service (`src/services/api.ts`)
- [ ] Create `useJob` hook (`src/hooks/useJob.ts`)
- [ ] Create `usePolling` hook (`src/hooks/usePolling.ts`)

### Phase 2: Components
- [ ] Create `FileUploader` component
- [ ] Create `ParameterEditor` component
- [ ] Create `ModeToggle` component
- [ ] Create `JobStatus` component
- [ ] Create `PlotViewer` component
- [ ] Create `ResultsViewer` component

### Phase 3: Integration
- [ ] Update `DashboardPage.tsx` with new components
- [ ] Connect job submission flow
- [ ] Implement status polling
- [ ] Implement download flow
- [ ] Test full workflow

### Phase 4: Polish
- [ ] Loading states
- [ ] Error handling
- [ ] Responsive design
- [ ] Animations

---

## Docker Compose Integration

The system runs via Docker Compose. Ensure the frontend service is configured:

```yaml
services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "5173:5173"
    environment:
      - VITE_API_BASE_URL=http://backend:8000
    depends_on:
      - backend
```

Build and run:
```bash
docker compose up --build
```

Access UI at: `http://localhost:5173`