# System Architecture & Data Flow Guide

## Visual Overview

```
YOUR COMPUTER
    │
    ├─→ Browser: http://localhost:8000/docs
    │        ↓
    │   FastAPI Swagger UI
    │   (Interactive testing)
    │
    └─→ Docker Container (sky130_eda)
           │
           ├─ FastAPI App (Port 8000)
           │  ├─ POST /api/v1/upload
           │  ├─ GET /api/v1/parameters
           │  ├─ POST /api/v1/submit
           │  └─ GET /api/v1/status
           │
           ├─ Backend Services
           │  ├─ Pipeline Executor
           │  ├─ Circuit Simulation
           │  └─ Result Parsing
           │
           ├─ AI Engine
           │  ├─ Optimizers (Bayesian, PSO, Random)
           │  ├─ Neural Surrogates
           │  ├─ Design Reasoner
           │  └─ Cache Layer
           │
           ├─ EDA Tools
           │  ├─ Ngspice (Simulator)
           │  ├─ Sky130 PDK (Devices)
           │  ├─ Magic (Layout)
           │  ├─ Netgen (LVS)
           │  └─ KLayout (Viewer)
           │
           └─ Storage
              ├─ /home/eda/data/designs
              ├─ /home/eda/data/cache
              └─ /home/eda/data/results
```

---

## Data Flow: One Complete Circuit Run

```
┌─────────────────────────────────────────────────────┐
│ Step 1: UPLOAD CIRCUIT FILE                         │
└─────────────────────────────────────────────────────┘

User: Selects my_circuit.py (1KB)
   ↓
POST /api/v1/upload
   ↓
Backend receives file
   ↓
Save to: /home/eda/data/designs/uploads/proc_xyz_my_circuit.py
   ↓
Return: {"process_id": "proc_xyz"}

Memory State:
processes["proc_xyz"] = {
    "status": "pending",
    "file_path": "/home/eda/data/designs/uploads/proc_xyz_my_circuit.py"
}

┌─────────────────────────────────────────────────────┐
│ Step 2: EXTRACT PARAMETERS (Parse Python File)     │
└─────────────────────────────────────────────────────┘

User: GET /api/v1/parameters/proc_xyz
   ↓
Backend: Read uploaded file
   ↓
Use AST (Abstract Syntax Tree) parser
   ↓
Find: PARAMETERS = { 'iref': 10e-6, 'W': 2.0, ... }
   ↓
Extract types and defaults
   ↓
Return:
{
    "process_id": "proc_xyz",
    "parameters": [
        {"name": "iref", "type": "float", "default": 1e-5},
        {"name": "W", "type": "float", "default": 2.0},
        {"name": "L", "type": "float", "default": 0.5}
    ]
}

┌─────────────────────────────────────────────────────┐
│ Step 3: SUBMIT PARAMETERS & START PROCESSING       │
└─────────────────────────────────────────────────────┘

User: POST /api/v1/submit/proc_xyz
      Body: {"iref": 1.5e-5, "W": 3.0, "L": 0.8}
   ↓
Backend: Store parameters
   ↓
Memory State Update:
processes["proc_xyz"] = {
    "status": "running",
    "progress": 5,
    "provided_parameters": {"iref": 1.5e-5, "W": 3.0, "L": 0.8}
}
   ↓
Background Task Starts:
   ├─ PipelineExecutor.run_circuit_from_file()
   │
   ├─ Step 3.1: Check Cache
   │    ├─ Look in: /home/eda/data/cache/designs/
   │    ├─ Key = "current_mirror_{iref=1.5e-05, W=3.0, L=0.8}"
   │    └─ Hit? Use cached result. Miss? Continue.
   │
   ├─ Step 3.2: Load uploaded file
   │    ├─ Read: /home/eda/data/designs/uploads/proc_xyz_my_circuit.py
   │    └─ Extract build_circuit() function (if exists)
   │
   ├─ Step 3.3: Generate Netlist
   │    ├─ Create SPICE netlist string
   │    ├─ Include Sky130 library: .include /opt/.../sky130.lib.spice
   │    ├─ Insert transistors: M1, M2, ...
   │    ├─ Apply parameters: W={W}u, L={L}u
   │    ├─ Add .op, .ac analysis commands
   │    └─ Save to: /home/eda/data/designs/proc_xyz.spice
   │
   ├─ Step 3.4: Run Ngspice Simulation
   │    ├─ Command: ngspice -b proc_xyz.spice -o proc_xyz.out
   │    ├─ Simulator reads netlist
   │    ├─ Loads Sky130 device models
   │    ├─ Runs operating point (.op)
   │    ├─ Runs AC analysis (.ac)
   │    └─ Output: /home/eda/data/results/proc_xyz.out
   │
   ├─ Step 3.5: Parse Results
   │    ├─ Extract from .out file:
   │    │  ├─ Operating point: Vgs, Id, Vds
   │    │  ├─ AC analysis: Gain, Bandwidth, Phase
   │    │  └─ Other measurements
   │    └─ Calculated values:
   │       ├─ gain_db = 20*log10(gain)
   │       └─ bandwidth_hz = -3dB frequency
   │
   ├─ Step 3.6: Cache Result
   │    └─ Save to: /home/eda/data/cache/designs/current_mirror_*.json
   │
   └─ Step 3.7: Update Status
       └─ processes["proc_xyz"] = {
           "status": "completed",
           "progress": 100,
           "results": {
               "netlist_path": "/home/eda/data/designs/proc_xyz.spice",
               "simulation_output": {
                   "operating_point": {...},
                   "ac_analysis": {...}
               }
           }
       }

┌─────────────────────────────────────────────────────┐
│ Step 4: CHECK STATUS & GET RESULTS                  │
└─────────────────────────────────────────────────────┘

User: GET /api/v1/status/proc_xyz (polls every 2 seconds)
   ↓
Backend: Look up processes["proc_xyz"]
   ↓
Return current state (progress, status, results if done)
   ↓
User: Sees progress 100 and final results
   ↓
Results contain:
{
    "netlist_path": "data/designs/proc_xyz.spice",
    "simulation_output": {
        "operating_point": {
            "vdd": 1.8,
            "id": 1.5e-5,
            "vgs": 0.65,
            "vout": 0.9
        },
        "ac_analysis": {
            "gain_db": 42.5,
            "bandwidth_hz": 900000.0,
            "phase_deg": -85.5
        }
    }
}
```

---

## File Locations & Purpose

```
HOST MACHINE
├─ /home/user/Desktop/Adnan/Analog_Tool-Automation/
│  ├─ backend/                      # API code
│  │  └─ app/
│  │     ├─ main.py                 # Starts API
│  │     ├─ api/circuits.py         # Endpoint definitions
│  │     ├─ models/circuit.py       # Data types
│  │     └─ services/pipeline_executor.py  # Execution logic
│  │
│  ├─ ai_engine/                    # Optimization AI
│  │  ├─ optimizers/
│  │  │  ├─ base_optimizer.py       # Base classes
│  │  │  └─ bayesian_optimizer.py   # Smart optimizer (NEW)
│  │  ├─ surrogates/mlp.py          # Neural network
│  │  ├─ reasoners/analog_reasoner.py  # Heuristics (NEW)
│  │  └─ cache/design_cache.py      # Caching (NEW)
│  │
│  ├─ docker/                       # Container config
│  │  ├─ Dockerfile                 # Ngspice only
│  │  └─ Dockerfile.sky130          # Full Sky130 + tools
│  │
│  └─ data/
│     ├─ designs/                   # Generated files
│     ├─ cache/                     # Result cache
│     └─ results/                   # Simulation output
│
DOCKER CONTAINER (sky130_eda)
├─ /home/eda/                       # Mirror of backend/
│  ├─ backend/
│  │  └─ app/                       # API files copied here
│  │
│  ├─ ai_engine/                    # AI engine files copied here
│  │
│  ├─ data/
│  │  ├─ designs/
│  │  │  ├─ uploads/               # User-uploaded files
│  │  │  └─ proc_xyz.spice         # Generated netlists
│  │  └─ cache/
│  │     └─ designs/               # Cached results (JSON)
│  │
│  └─ tests/                        # Test files
│
├─ /opt/eda-venv/                   # Python environment
│  └─ lib/python3.12/site-packages/
│     └─ (all dependencies: numpy, torch, scipy, etc.)
│
├─ /opt/open_pdks/sky130/sky130A/   # Sky130 PDK
│  ├─ libs.tech/ngspice/
│  │  ├─ sky130.lib.spice           # Device models
│  │  └─ corners/                   # Process corners
│  │
│  └─ libs.ref/                     # Reference files
│
├─ /usr/local/bin/
│  ├─ ngspice                       # Simulator executable
│  ├─ magic                         # Layout tool
│  ├─ netgen                        # LVS tool
│  └─ klayout                       # Viewer
│
└─ /tmp/api.log                     # API logs
```

---

## Component Responsibilities

### 1. FastAPI Backend (`backend/app/`)

**Responsibility:** Accept HTTP requests and manage workflows

**Key Files:**
- `main.py` — Start Uvicorn server on port 8000
- `api/circuits.py` — Define all endpoints
- `models/circuit.py` — Pydantic data models
- `services/pipeline_executor.py` — Run circuits

**Flow:**
```
HTTP Request → Route Handler → Pipeline Executor → Response
```

---

### 2. Pipeline Executor (`backend/app/services/pipeline_executor.py`)

**Responsibility:** Generate netlist and run simulation

**Steps:**
1. Parse uploaded Python file
2. Extract `PARAMETERS` dict
3. Generate SPICE netlist string
4. Write netlist to `.spice` file
5. Run Ngspice binary
6. Parse `.out` file for results
7. Cache results
8. Update process status

**Execution Time:** 1-5 seconds per circuit

---

### 3. AI Engine

#### 3.1 Optimizers (`ai_engine/optimizers/`)

**Responsibility:** Find best parameters automatically

**Available Methods:**
- `GridSearchOptimizer` — Try all grid points
- `RandomSearchOptimizer` — Random sampling
- `ParticleSwarmOptimizer` — Swarm intelligence
- `NeuralTurboOptimizer` — Neural surrogate + trust region
- `BayesianOptimizer` — **Smart (NEW)** — Expected Improvement

**Usage:**
```python
optimizer = create_optimizer(OptimizationMethod.BAYESIAN_NN, ...)
result = optimizer.optimize(circuit_simulator)
# Calls circuit_simulator 30-50 times (vs 100+ random)
```

---

#### 3.2 Surrogates (`ai_engine/surrogates/mlp.py`)

**Responsibility:** Fast approximation of circuit behavior

**How it Works:**
```
Training Phase:
  Input: Parameters (W, L, ...)
  Output: Performance (gain, bandwidth, ...)
  Network: 5 parallel MLPs for uncertainty

Prediction Phase:
  Input: New parameters
  Output: Predicted performance + confidence
  Time: 1ms (vs 2s for real sim)
```

**Used By:** Bayesian optimizer for candidate search

---

#### 3.3 Reasoner (`ai_engine/reasoners/analog_reasoner.py`) — NEW

**Responsibility:** Encode analog design knowledge

**Capabilities:**
- `estimate_gain_from_gm_id()` — gm/ID methodology
- `estimate_bandwidth()` — Frequency response
- `suggest_initial_parameters()` — Smart initialization
- `validate_design_constraints()` — Sky130 DRC
- `suggest_optimization_hints()` — Real-time feedback

**Example:**
```python
# Instead of random W/L, start smart
hints = AnalogReasoner.suggest_initial_parameters("opamp", specs)
# → {"W_diff": 7.5, "L_diff": 0.5, ...}  # Not random!
```

---

#### 3.4 Cache (`ai_engine/cache/design_cache.py`) — NEW

**Responsibility:** Avoid redundant simulations

**How it Works:**
```
1. Hash parameters → cache key
2. Check if key exists in /home/eda/data/cache/designs/
3. Hit? Return instantly
4. Miss? Run simulation, save result
```

**Speed Gain:** 10-30% (for repeated parameters)

---

### 4. Ngspice (In Container)

**Responsibility:** Real circuit simulation

**Inputs:**
- `.spice` file (netlist)
- Sky130 device models
- Analysis commands (.op, .ac)

**Process:**
1. Read netlist
2. Load Sky130 models (transistors, resistors, caps)
3. Build matrices
4. Solve equations (DC → AC)
5. Output results to `.out` file

**Execution Time:** 1-5 seconds per circuit

---

## Memory State During Optimization

```
Initial State:
processes = {}

After Upload:
processes = {
    "proc_xyz": {
        "status": "pending",
        "progress": 0,
        "file_path": "/home/eda/data/designs/uploads/proc_xyz_circuit.py",
        "created_at": "2026-02-05T12:34:56",
        "results": None
    }
}

After Submit:
processes = {
    "proc_xyz": {
        "status": "running",
        "progress": 10,
        "provided_parameters": {"W": 3.0, "L": 0.8, ...},
        "created_at": "2026-02-05T12:34:56",
        "results": None
    }
}

During Optimization (Bayesian):
processes = {
    "proc_xyz": {
        "status": "running",
        "progress": 45,
        "optimization_state": {
            "iteration": 15,
            "best_score": 2.3,
            "best_params": {"W": 5.2, "L": 0.6},
            "evaluation_count": 18
        }
    }
}

After Completion:
processes = {
    "proc_xyz": {
        "status": "completed",
        "progress": 100,
        "results": {
            "netlist_path": "data/designs/proc_xyz.spice",
            "simulation_output": {
                "operating_point": {...},
                "ac_analysis": {...}
            }
        }
    }
}
```

---

## Typical Timing

```
Event                          Time
─────────────────────────────────────
1. File Upload                 0.1s
2. Parameter Extraction        0.1s
3. Parameter Submission        0.05s
4. Single Circuit Sim          2-5s
   ├─ Generate netlist         0.1s
   ├─ Run Ngspice              1-4s
   └─ Parse results            0.1s
5. Bayesian Opt (30 evals)     2min
   ├─ Initial samples (10)     20-50s
   ├─ Surrogate training       10s
   ├─ Candidate search         5s
   └─ Real evaluations (20)    40-100s
6. Random Search (100 evals)   10min
   └─ Just try random values   100 × 2-5s

SPEEDUP: Bayesian = 3-5x faster
```

---

## Security Notes

✅ **Safe by Design:**
- User Python files **not executed** — only parsed (AST)
- No `eval()` or `exec()` — only reads PARAMETERS dict
- Netlist is plain text — validated before Ngspice
- All files sandboxed in container

---

## Extension Points

Want to add features? Hook into these:

| Point | File | How |
|-------|------|-----|
| New circuit type | `analog_reasoner.py` | Add to `suggest_initial_parameters()` |
| New optimizer | `create_optimizer()` | Add new OptimizationMethod enum + class |
| Caching strategy | `design_cache.py` | Override `_make_key()` method |
| Post-processing | `pipeline_executor.py` | Hook after `parse_results()` |
| Constraints | `base_optimizer.py` | Add to ObjectiveSpec |

---

## Summary

```
User → Browser (Swagger UI)
   ↓
HTTP Request → FastAPI (Port 8000)
   ↓
Pipeline Executor
   ├─ Load Python file
   ├─ Generate netlist
   ├─ Run Ngspice (2-5s)
   └─ Parse results
   ↓
Cache Layer (optional speedup)
   ├─ Hit? Return cached
   └─ Miss? Store new
   ↓
AI Engine (optional optimization)
   ├─ Surrogate predicts fast
   ├─ Bayesian picks next candidate
   └─ Repeat 20-50 times
   ↓
Response → Browser
   ↓
User sees results (gain, bandwidth, etc.)
```

**All running in Docker container with Sky130 PDK + Ngspice.** ✅
