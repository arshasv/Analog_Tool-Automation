# xEDA: AI-Driven Analog & Mixed-Signal Design Platform

![xEDA Header](https://raw.githubusercontent.com/arshasv/Analog_Tool-Automation/main/docs/header.png)

xEDA is a modern, containerized platform for automated analog and mixed-signal circuit design. It bridges the gap between high-level Python circuit descriptions and low-level SPICE physics, providing a unified pipeline for simulation, parametric analysis, and automated visualization using the Sky130 PDK.

---

## 🚀 Key Features

-   **True Physics Simulation**: Powered by `ngspice`, delivering real-world DC, AC, and Transient analysis. No synthetic data.
-   **Sky130 PDK Integration**: Built-in support for Sky130 MOSFETs (1.8V) and PNP BJTs with realistic parasitic modeling.
-   **Unified Analysis Pipeline**: Automatically rectifies netlists, manages PDK paths, and strips legacy control blocks for clean simulation.
-   **Metadata-Driven Workflow**: Use simple comments like `@AC_EXPR` or `@TRAN_EXPR` to control complex simulation and plotting logic.
-   **High-Fidelity Visualization**: Automatic generation of Bode plots, I-V curves, and transient waveforms with realistic physical effects (settling, bandwidth roll-off).
-   **Rich Circuit Library**: 20+ pre-configured templates including Op-Amps, LDOs, Bandgaps, PLL building blocks, and standard CMOS logic.

---

## 🏗️ System Architecture & Flow

xEDA follows a strictly deterministic pipeline to ensure simulation accuracy:

1.  **Input**: User uploads a Python circuit definition (e.g., `current_mirror.py`).
2.  **Orchestration (`AnalysisOrchestrator`)**:
    *   Extracts metadata hints (`@AC_EXPR`, etc.).
    *   Generates three specialized netlists (DC, AC, Transient).
    *   Injects parametric variables (Width, Length, Current) and fixes PDK includes.
3.  **Execution (`NgSpiceExecutor`)**:
    *   Runs `ngspice` in batch mode.
    *   Captures raw simulation logs and exports data to high-precision ASCII/CSV files.
4.  **Visualization (`Plotting`)**:
    *   Parses CSV data, mapping physical vectors to X/Y axes.
    *   Applies intelligent labeling and scaling.
5.  **Packaging**: Compiles netlists, logs, and plots into a single downloadable ZIP.

---

## 🛠️ Installation & Setup

### Prerequisites
-   Docker and Docker Compose installed.

### Quick Start
```bash
# Clone the repository
git clone https://github.com/arshasv/Analog_Tool-Automation.git
cd xEDA

# Build and start the platform
docker compose down
docker compose build --no-cache
docker compose up -d
```
The API will be available at `http://localhost:8000`.

---

## 📖 API Usage

### Run a Simulation
**Endpoint**: `POST /api/v1/run`

**Parameters**:
-   `file`: The `.py` or `.spice` circuit file.
-   `parameters`: (Optional) JSON string of circuit parameters (e.g., `{"width": 5.0, "i_tail": 20}`).

### Check Status
**Endpoint**: `GET /api/v1/status/{process_id}`

### Download Results
**Endpoint**: `GET /api/v1/download/{process_id}`

---

## 📝 Circuit Authoring Guide

To make a circuit compatible with the xEDA automated plotter, include these metadata hints in your netlist comments:

```python
netlist = """* My Circuit
* @AC_SOURCE: Vin
* @AC_EXPR: vdb(vout)
* @TRAN_EXPR: v(vout)
* @DC_EXPR: v(vout)
.lib "{lib_path}" tt
...
"""
```

-   **`@AC_SOURCE`**: The voltage/current source used for frequency sweeps.
-   **`@AC_EXPR`**: The expression for the Bode plot (usually `vdb(node)` or `db(i(source))`).
-   **`@TRAN_EXPR`**: The vector to plot over time.
-   **`@DC_EXPR`**: The variable to plot against the sweep variable.

---

## 📂 Project Structure

```text
xEDA/
├── app/
│   ├── api/            # FastAPI Route Definitions
│   ├── circuits/       # 20+ Circuit Templates (Current Mirrors, OpAmps, etc.)
│   ├── core/           # Config and Logging
│   ├── services/       # The Core Engine (Orchestrator, Executor)
│   └── utils/          # Plotting and GDS Export Utilities
├── pdk/                # Bundled Sky130 Fallback Models
├── data/               # Simulation Workspace (Process IDs)
├── Dockerfile          # Multi-stage build for NGSpice/Python
└── docker-compose.yml  # Environment Orchestration
```

---

## ⚖️ License
This project is licensed under the MIT License - see the LICENSE file for details.
