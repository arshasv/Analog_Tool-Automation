# 🌌 xEDA: AI-Driven Analog & Mixed-Signal Platform

## 📌 Project Overview
**xEDA** is a state-of-the-art, containerized platform designed for automated analog circuit design. It bridges the gap between high-level Pythonic circuit descriptions and low-level SPICE physics, specifically optimized for the **Sky130 Open-Source PDK**.

The platform provides a unified pipeline for simulation, parametric analysis, and automated visualization, enabling designers to focus on topology and specs while the system handles the heavy lifting of SPICE orchestration.

---

## 🏗️ System Architecture

### 🛡️ Backend (FastAPI Control Plane)
The heart of xEDA is a **FastAPI** backend that acts as the control plane for the entire EDA stack.
- **Core Engine**: Located in `app/`.
- **API Documentation**: Interactive docs available at `/docs` (Swagger UI).
- **Service Layer**: Asynchronous execution of simulation pipelines via `BackgroundTasks`.

### 🖥️ Frontend & Integration Workflow
The system is built with an **API-First** philosophy, allowing it to be integrated into web dashboards, CLI tools, or CI/CD pipelines. The standard "frontend-to-backend" lifecycle consists of:

1.  **🔍 Initialization**: The client selects or uploads a Python-based circuit template.
2.  **🚀 Execution (`POST /api/v1/run`)**:
    - The client sends a circuit file (`.py`) and design parameters (width, length, bias).
    - The backend generates a tracking `process_id`.
3.  **📡 Polling (`GET /api/v1/status/{process_id}`)**:
    - The client tracks real-time progress. The pipeline reports logs and status changes (Pending → Running → Completed).
4.  **📦 Retrieval (`GET /api/v1/download/{process_id}`)**:
    - A consolidated ZIP bundle is returned, containing optimized netlists, high-fidelity PNG plots, and performance metrics.

---

## ⚙️ The Simulation Pipeline: Core Python Files

The "intelligence" of the platform resides in `app/services/`. These specialized modules work in concert to transform a script into a physical result:

### 1. 📂 `pipeline_executor.py` (The Orchestrator)
The entry point for all operations. It handles:
- **Parameter Extraction**: Uses Python's `ast` module to read default parameters from uploaded files without executing them.
- **State Management**: Tracks simulation progress and stores results in a persistent memory (`data/results/design_memory.jsonl`).

### 2. 🎼 `analysis_orchestrator.py` (The Director)
Translates high-level circuit intent into specialized SPICE netlists.
- **Analysis Splitting**: It intelligently splits a single circuit definition into three distinct netlists (DC, AC, Transient) to prevent analysis command interference.
- **Metadata Parsing**: Looks for markers like `@AC_SOURCE` or `@TRAN_EXPR` to configure the simulation sweep ranges automatically.

### 3. ⚡ `ngspice_executor.py` (The Engine)
The low-level driver for the **Ngspice** binary.
- **Process Spawning**: Runs SPICE in batch mode within the container environment.
- **Data Parsing**: Converts raw high-precision simulation logs into structured Python dictionaries for further analysis.

### 4. 🧬 `architecture_synthesizer.py` & `topology.py` (The Architect)
Provides logic for **Architecture Search**.
- **`topology.py`**: Defines a "Role-Based" system (Input, Gain, Load, etc.) and enforces physical constraints (e.g., "telescopic cascode requires wide-swing bias").
- **`architecture_synthesizer.py`**: Programmatically generates functional SPICE netlists based on selected topology roles.

### 5. 📏 `parameter_synthesizer.py` (The Optimizer)
Ensures designs are physically realistic.
- **DRC-Safe Clamping**: Clamps all transistor dimensions (W, L) to valid **Sky130** limits (e.g., $W_{min} = 0.42\mu m$).
- **Analytical Sizing**: Uses first-order analog equations to provide a "good" starting point for design variables based on target gain or bandwidth.

### 6. 📈 `utils/plotting.py` (The Visualizer)
Generates publication-quality waveforms.
- **Automated Scaling**: Maps simulation vectors to readable axes (dB, Magnitude, Seconds).
- **Multi-Analysis Support**: Generates Bode plots for AC, I-V curves for DC, and Settling Waveforms for Transient analysis.

---

## 📂 Circuit Library (`app/circuits`)
This directory contains 20+ optimized templates. 
- **Upload Flow**: Users can upload these files to the `/run` endpoint. 
- **Standardization**: Each file follows a standard `generate_netlist(**kwargs)` signature, making them fully compatible with the automated synthesis tools.

---

## 🧪 Parameter Introspection Workflow

To make it easy to discover and reuse circuit defaults without manually reading each Python file, xEDA exposes a **parameter introspection** API that uses the same AST-based parser as the simulation pipeline:

- **Introspect Parameters**  
    **Endpoint**: `POST /api/v1/introspect`  
    **Body**: form-data with a single field `file` containing a circuit `.py` file (e.g. `two_stage_opamp.py`).  
    **Response**:
    ```json
    {
        "parameters": {
            "w_diff": 8,
            "w_load": 16,
            "cc": 2,
            "i_tail": 80
        }
    }
    ```

- **Run with Parameters**  
    Copy the returned `parameters` object and paste it (optionally edited) into the `parameters` field of `POST /api/v1/run` as a JSON string. This guarantees that the values match the circuit's `generate_netlist(...)` signature and any embedded `PARAMETERS` / `DEFAULT_PARAMS` dicts.

This flow lets a user: *(1) upload a circuit once to discover sane defaults, (2) tweak the JSON, and (3) immediately re-simulate with the modified parameter set.*

---

## 🐳 Deployment & PDK
- **Containerization**: The entire stack is packaged in Docker, ensuring exact versions of `ngspice` and `magic/klayout`.
- **Sky130 Integration**: The backend automatically injects the correct PDK library paths into generated netlists, leveraging the high-accuracy BSIM4 models.
