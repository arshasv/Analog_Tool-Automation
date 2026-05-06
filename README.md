# xEDA: Analog Design Automation Platform

xEDA is a comprehensive, full-stack automation platform designed to streamline the analog circuit design cycle. It integrates industry-standard simulation engines with robust mathematical optimization algorithms and a high-fidelity web interface to accelerate design exploration and performance centering.

---

## 🚀 Core Features

### 1. **Automated Simulation Pipeline**
*   **Engine:** Powered by NGSpice for high-performance analog simulation.
*   **PDK Integration:** Native support for the **SkyWater 130nm (SKY130) PDK**.
*   **Analyses:** Seamless execution of DC Operating Point, AC Frequency Response, and Transient Analysis.

### 2. **Professional Optimization Strategy**
*   **Two-Stage Search:** Implements a rigorous optimization flow:
    1.  **Coarse Global Search:** Random sampling across the design space to identify promising regions.
    2.  **Local Refinement:** Uses the **Nelder-Mead (Simplex)** algorithm for precise gradient-free convergence towards performance targets.
*   **Parameter Synthesis:** Automatically optimizes transistor sizing (W, L) to meet specific design constraints.
*   **Cost-Function Centering:** Multi-objective optimization based on weighting gain, current, and power consumption.

### 3. **Modern Circuit Library**
A growing collection of introspectable Python templates for common analog blocks:
*   **Primitives:** Current Mirrors (standard, Wilson, Cascode), PMOS variants.
*   **Amplifiers:** Common Source, Common Gate, Source Follower, Cascode Amplifiers.
*   **Differential Nodes:** Two-Stage OpAmps, Folded Cascode OTAs, Differential Pairs.
*   **Stability & Synthesis:** Bandgap References, LDO Regulators, Level Shifters, Ring Oscillators, and Schmitt Triggers.

### 4. **Intuitive Workflow UI**
*   **Dashboard-Centric:** Real-time monitoring of simulation status and optimization progress.
*   **Parameter Editor:** Context-aware inputs for circuit variables with built-in validation.
*   **Results Viewer:** High-fidelity data visualization, performance metric filtering, and raw payload inspection.

---

## 🛠 Tech Stack

### Backend (Python/FastAPI)
*   **Framework:** FastAPI for high-concurrency API management.
*   **Algorithms:** SciPy-based **Nelder-Mead** implementation for robust circuit optimization.
*   **Numerical:** NumPy and SciPy for data processing and mathematical modeling.
*   **Simulation:** PySpice wrapper for NGSpice integration.

### Frontend (React/TypeScript)
*   **Core:** React 18 with TypeScript for type-safe UI development.
*   **Build Tool:** Vite for instantaneous development feedback.
*   **Styling:** Custom CSS-variable system supporting professional dark-mode aesthetics.

---

## 📦 Getting Started

### Prerequisites
*   [Docker](https://www.docker.com/) & [Docker Compose](https://docs.docker.com/compose/)
*   Sky130 PDK (Standardized path: `/opt/sky130_pdk/sky130A`)

### Installation & Launch

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/adnanfez/xEDA.git
    cd xEDA
    ```

2.  **Start Services:**
    ```bash
    docker compose up --build
    ```

3.  **Access the Platform:**
    *   **Frontend:** [http://localhost:5173](http://localhost:5173)
    *   **API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 📂 Project Structure

```text
xEDA/
├── app/                # FastAPI Backend 
│   ├── circuits/       # Python-based circuit templates
│   ├── core/           # Nelder-Mead Optimization core
│   ├── services/       # Orchestration & SPICE execution
│   └── utils/          # Data processing & plotting
├── frontend/           # React TypeScript Frontend
├── data/               # Persistent simulation results
└── pdk/                # SKY130 PDK definitions (mapped)
```

---

## 📄 License
This project is for academic research. Please refer to the SkyWater PDK license for foundry-related usage guidelines.
