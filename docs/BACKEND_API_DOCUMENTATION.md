# Backend & Backend API Documentation

## Table of Contents
1. [Overview](#overview)
2. [Tech Stack](#tech-stack)
3. [Project Structure](#project-structure)
4. [API Endpoints](#api-endpoints)
5. [Data Models](#data-models)
6. [Services](#services)
7. [Configuration](#configuration)
8. [Circuit Templates](#circuit-templates)

---

## Overview

xEDA is an AI-Driven Analog Circuit Design Automation Platform that enables circuit simulation and optimization using ngspice. The backend provides RESTful APIs for uploading circuit files, running simulations/optimizations, and retrieving results.

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Framework | Python FastAPI |
| Server | Uvicorn |
| Database | SQLAlchemy (SQLite/PostgreSQL) |
| Task Queue | Celery + Redis (configured) |
| Simulation | NgSpice |
| Optimization | pymoo, DEAP, optuna, scikit-learn |
| Frontend | Vue.js/Vite |

---

## Project Structure

```
app/
├── main.py                  # FastAPI app entry point
├── api/                     # API route definitions
│   └── circuits.py          # All circuit-related endpoints
├── core/                    # Core configuration & optimization
│   ├── config.py            # Settings/environment config
│   └── optimization/        # W/L optimization modules
│       ├── optimizer.py     # Main optimizer (coarse + Nelder-Mead)
│       ├── cost_function.py # Cost computation
│       └── param_update.py  # W/L parameter handling
├── models/                  # Data models/schemas
│   └── circuit.py           # Pydantic models
├── services/                # Business logic
│   ├── pipeline_executor.py # Main orchestrator
│   ├── analysis_orchestrator.py # DC/AC/Tran netlist generation
│   ├── ngspice_executor.py  # NgSpice execution & parsing
│   ├── topology.py          # Circuit topology definitions
│   ├── architecture_synthesizer.py # Netlist generation
│   └── parameter_synthesizer.py    # Parameter handling
├── circuits/                # Circuit templates (20+)
│   ├── primitives/          # Basic components (MOS, resistor, etc.)
│   ├── macros/              # Complex blocks (OpAmps, comparators)
│   ├── bricks/              # Building blocks
│   ├── io/                  # I/O circuits
│   └── mixed_signal/        # Mixed-signal circuits
└── utils/                   # Utility functions
    └── plotting.py          # Matplotlib plotting functions
```

---

## API Endpoints

### Base URL
```
http://localhost:8000/api/v1
```

### Endpoints

| Method | Path | Handler | Description |
|--------|------|---------|-------------|
| `GET` | `/` | `root()` | Root endpoint returning API info |
| `GET` | `/health` | `health()` | Health check endpoint |
| `POST` | `/api/v1/run` | `run_circuit()` | Upload circuit file and run simulation/optimization |
| `GET` | `/api/v1/status/{process_id}` | `get_status()` | Check simulation status and retrieve results |
| `GET` | `/api/v1/download/{process_id}` | `download_results()` | Download ZIP with netlists, plots, and metrics |
| `POST` | `/api/v1/introspect` | `introspect_circuit()` | Extract default parameters from circuit file |

---

### POST /api/v1/run

Upload a circuit file and run simulation or optimization.

**Request:**
- **Content-Type:** `multipart/form-data`
- **Form Fields:**
  - `file` (required): Circuit `.py` or `.spice` file
  - `parameters` (optional): JSON string of circuit parameters
  - `mode` (optional): `"simulate"` or `"optimize"` (default: `"simulate"`)

**Response:**
```json
{
  "process_id": "uuid-string",
  "filename": "circuit.py",
  "status": "PENDING",
  "parameters": {},
  "mode": "simulate",
  "message": "Circuit submitted successfully"
}
```

---

### GET /api/v1/status/{process_id}

Check simulation status and retrieve results.

**Path Parameters:**
- `process_id`: The ID returned from `/run`

**Response:**
```json
{
  "process_id": "uuid-string",
  "filename": "circuit.py",
  "status": "COMPLETED",
  "progress": 100,
  "parameters": {},
  "mode": "simulate",
  "results": {...},
  "error": null,
  "created_at": "2026-04-20T10:00:00",
  "updated_at": "2026-04-20T10:05:00"
}
```

**Status Values:**
- `PENDING`: Task queued
- `RUNNING`: Simulation in progress
- `COMPLETED`: Successfully finished
- `FAILED`: Error occurred

---

### GET /api/v1/download/{process_id}

Download ZIP file containing results.

**Path Parameters:**
- `process_id`: The ID returned from `/run`

**Response:**
- Returns a ZIP file with:
  - Netlists (`.sp`)
  - Plot images (`.png`)
  - Summary JSON (`summary.json`)

---

### POST /api/v1/introspect

Extract default parameters from a circuit file.

**Request:**
- **Content-Type:** `multipart/form-data`
- **Form Fields:**
  - `file` (required): Circuit `.py` file to analyze

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

## Data Models

Defined in `/home/user/Desktop/Adnan/xEDA/app/models/circuit.py`

### ProcessStatus (Enum)
```python
class ProcessStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
```

### CircuitRequest
```python
class CircuitRequest(BaseModel):
    circuit_type: str
    parameters: Dict[str, Any]
```

### ProcessState
```python
class ProcessState(BaseModel):
    process_id: str
    status: ProcessStatus
    progress: int = 0
    created_at: datetime
    updated_at: datetime
    results: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
```

### ParameterSpec
```python
class ParameterSpec(BaseModel):
    name: str
    type: str
    default: Any
    description: str
```

### RunResponse
```python
class RunResponse(BaseModel):
    process_id: str
    filename: str
    status: ProcessStatus
    parameters: Dict[str, Any]
    mode: str
    message: str
```

### StatusResponse
```python
class StatusResponse(BaseModel):
    process_id: str
    filename: str
    status: ProcessStatus
    progress: int
    parameters: Dict[str, Any]
    mode: str
    results: Optional[Dict[str, Any]]
    error: Optional[str]
    created_at: datetime
    updated_at: datetime
```

---

## Services

### PipelineExecutor
**File:** `/home/user/Desktop/Adnan/xEDA/app/services/pipeline_executor.py`

Main orchestrator for circuit execution.

| Method | Purpose |
|--------|---------|
| `parse_parameters_from_file()` | AST-based parameter extraction from circuit files |
| `run_circuit_from_file()` | Main execution flow (simulate or optimize) |
| `run_architecture_search()` | Architecture search mode |
| `_store_design_memory()` | Persist design points to JSONL |

### AnalysisOrchestrator
**File:** `/home/user/Desktop/Adnan/xEDA/app/services/analysis_orchestrator.py`

Generates DC, AC, and Transient netlists for simulation.

### NgSpiceExecutor
**File:** `/home/user/Desktop/Adnan/xEDA/app/services/ngspice_executor.py`

Executes ngspice simulations and parses output.

### WLOptimizer
**File:** `/home/user/Desktop/Adnan/xEDA/app/core/optimization/optimizer.py`

Two-stage W/L optimization:
1. Coarse search
2. Nelder-Mead refinement

---

## Configuration

**File:** `/home/user/Desktop/Adnan/xEDA/app/core/config.py`

| Setting | Default | Description |
|---------|---------|-------------|
| `APP_NAME` | "AI-Driven Sky130 ASIC Platform" | Application name |
| `APP_VERSION` | "0.1.0" | Version |
| `DEBUG` | True | Debug mode |
| `API_V1_PREFIX` | "/api/v1" | API prefix |
| `HOST` | "0.0.0.0" | Server host |
| `PORT` | 8000 | Server port |
| `DATABASE_URL` | "sqlite:///./data/platform.db" | Database connection |
| `REDIS_URL` | "redis://localhost:6379/0" | Redis connection |
| `PDK_ROOT` | "/opt/sky130_pdk" | Sky130 PDK root |
| `NGSPICE_BIN` | "/usr/local/bin/ngspice" | NgSpice binary path |
| `WORK_DIR` | "./data/designs" | Working directory |
| `MAX_OPTIMIZATION_ITERATIONS` | 100 | Max optimization iterations |
| `OPTIMIZATION_TIMEOUT` | 3600 | Timeout in seconds |

---

## Circuit Templates

Located in `/home/user/Desktop/Adnan/xEDA/app/circuits/`

### Categories
- **primitives/**: Basic components (MOS, resistor, capacitor, etc.)
- **macros/**: Complex blocks (OpAmps, comparators, bandgaps)
- **bricks/**: Building blocks
- **io/**: I/O circuits
- **mixed_signal/**: Mixed-signal circuits

---

## Interactive API Documentation

FastAPI provides built-in interactive documentation:

- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

---

## Notes

- **Authentication:** Not implemented (API is open)
- **Middleware:** None custom middleware implemented
- **Database:** Process state stored in-memory (not persistent)
- **Task Queue:** Celery configured but not actively used
