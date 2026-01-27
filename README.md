# 🚀 AI-Driven Sky130 ASIC Platform

> **Revolutionary analog IC design automation powered by AI and open-source EDA tools**

![Version](https://img.shields.io/badge/version-0.1.0-blue)
![PDK](https://img.shields.io/badge/PDK-Sky130A-green)
![License](https://img.shields.io/badge/license-Apache%202.0-orange)

---

## 🎯 Vision

Transform the analog IC design workflow from manual, iterative processes to an **AI-powered, automated platform** that:

- ✅ Uses **real Sky130 PDK models** (not generic components)
- ✅ Integrates full **open-source EDA stack** (Ngspice, Magic, KLayout, Netgen)
- ✅ Provides **AI-driven parameter optimization** for circuit sizing
- ✅ Enables **automated layout generation and LVS verification**
- ✅ Offers **RESTful API** for programmatic design automation
- ✅ Runs entirely in **containerized Docker environment**

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   FastAPI Backend (Control Plane)           │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────┐  │
│  │ Circuits │ Simulate │  Layout  │  Verify  │ Optimize │  │
│  └──────────┴──────────┴──────────┴──────────┴──────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │
          ┌──────────────┼──────────────┐
          │              │              │
┌─────────▼────────┐ ┌───▼────────┐ ┌──▼─────────────┐
│  Circuit Library │ │ EDA Tools  │ │  AI Engine     │
│  - OpAmp         │ │ - Ngspice  │ │ - Optimizers   │
│  - Comparator    │ │ - Magic    │ │ - Reasoners    │
│  - Current Mirror│ │ - KLayout  │ │ - ML Models    │
│  - Bandgap       │ │ - Netgen   │ │                │
└──────────────────┘ └────────────┘ └────────────────┘
          │                  │              │
          └──────────────────┴──────────────┘
                         │
              ┌──────────▼──────────┐
              │   Sky130 PDK        │
              │   /opt/sky130_pdk   │
              └─────────────────────┘
```

---

## 📦 Technology Stack

### **PDK & EDA Tools**
- **Sky130 PDK**: Google/SkyWater 130nm open-source process
- **Ngspice 39**: SPICE circuit simulator with XSPICE & CIDER
- **Magic VLSI**: Layout editor and DRC checker
- **KLayout**: Layout viewer with Python API
- **Netgen**: LVS (Layout vs Schematic) verification

### **Backend**
- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: Database ORM
- **Celery + Redis**: Distributed task queue
- **PostgreSQL**: Production database

### **AI & Optimization**
- **Particle Swarm Optimization (PSO)**
- **Genetic Algorithms (DEAP)**
- **Bayesian Optimization (Optuna)**
- **PyTorch**: Deep learning framework

### **Infrastructure**
- **Docker**: Containerization
- **Docker Compose**: Multi-service orchestration

---

## 🚀 Quick Start

### **1. Clone Repository**
```bash
git clone <repository-url>
cd analog-eda
```

### **2. Build Docker Image**
```bash
cd docker
docker-compose build
```

**Note**: Initial build will take 30-60 minutes due to:
- Sky130 PDK download (~2GB)
- Magic, KLayout, Netgen compilation
- Python dependencies installation

### **3. Start Platform**
```bash
docker-compose up -d
```

### **4. Enter Container**
```bash
docker exec -it sky130_eda bash
```

### **5. Run Example Circuit**
```bash
# Sky130 RC circuit
cd circuits/library
python3 rc_sky130_example.py
ngspice sky130_rc.spice

# Current mirror
cd current_mirror
python3 sky130_current_mirror.py
ngspice sky130_current_mirror.spice
```

### **6. Start FastAPI Backend**
```bash
cd /home/eda/backend
python3 -m app.main
```

Access API at: `http://localhost:8000`

---

## 📁 Project Structure

```
analog-eda/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── main.py            # Main application
│   │   ├── core/              # Configuration
│   │   ├── api/               # API routes
│   │   ├── services/          # Business logic
│   │   └── models/            # Data models
│   └── requirements.txt
│
├── circuits/                   # Circuit library
│   ├── sky130/
│   │   └── devices.py         # Sky130 primitives
│   ├── library/
│   │   ├── opamp/
│   │   ├── comparator/
│   │   ├── current_mirror/
│   │   └── bandgap/
│   └── generators/            # Parameterized generators
│
├── ai_engine/                  # AI optimization
│   ├── optimizers/            # Optimization algorithms
│   ├── reasoners/             # Design reasoning
│   └── models/                # ML models
│
├── tools/                      # EDA tool wrappers
│   ├── simulation/            # Ngspice wrapper
│   ├── layout/                # Magic/KLayout automation
│   └── verification/          # DRC/LVS automation
│
├── docker/                     # Docker configuration
│   ├── Dockerfile.sky130      # Enhanced Dockerfile
│   ├── docker-compose.yml     # Multi-service config
│   └── ngspice-39/            # Ngspice source
│
├── data/                       # Working data
│   ├── designs/
│   ├── results/
│   └── cache/
│
└── tests/                      # Test suites
    ├── unit/
    └── integration/
```

---

## 🔧 API Endpoints

### **Platform Info**
```bash
GET /                          # Platform information
GET /health                    # Health check
GET /api/v1/info              # Detailed info
```

### **Circuit Design** (Coming Soon)
```bash
POST /api/v1/circuits/generate     # Generate circuit netlist
GET  /api/v1/circuits/library      # List available circuits
GET  /api/v1/circuits/{id}         # Get circuit details
```

### **Simulation** (Coming Soon)
```bash
POST /api/v1/simulate              # Run simulation
GET  /api/v1/simulate/{job_id}     # Get simulation results
```

### **Optimization** (Coming Soon)
```bash
POST /api/v1/optimize              # Start optimization
GET  /api/v1/optimize/{job_id}     # Get optimization status
```

---

## 💡 Examples

### **Example 1: Sky130 RC Circuit**
```python
from circuits.sky130.devices import resistor, capacitor

# Create Sky130 devices
r1 = resistor(name="1", resistance=10e3)  # 10kΩ
c1 = capacitor(name="1", capacitance=10e-12)  # 10pF

# Generate netlist with Sky130 models
circuit = Sky130RCCircuit(resistance=10e3, capacitance=10e-12)
circuit.generate_netlist()
```

### **Example 2: Current Mirror with Optimization**
```python
from ai_engine.optimizers.base_optimizer import (
    ParameterSpace, ObjectiveSpec, create_optimizer,
    OptimizationMethod
)

# Define parameter space
params = [
    ParameterSpace(name="width", min_value=1.0, max_value=10.0),
    ParameterSpace(name="length", min_value=0.5, max_value=2.0),
]

# Define objectives
objectives = [
    ObjectiveSpec(name="iout", target=10e-6, weight=1.0),
    ObjectiveSpec(name="area", target=0, minimize=True, weight=0.5),
]

# Create optimizer
optimizer = create_optimizer(
    method=OptimizationMethod.PARTICLE_SWARM,
    parameter_spaces=params,
    objectives=objectives,
    max_iterations=50
)

# Run optimization
result = optimizer.optimize(objective_function)
```

---

## 🎓 Circuit Library

### **Currently Implemented**
- ✅ RC Circuit (Sky130)
- ✅ Current Mirror (NMOS/PMOS)

### **Planned**
- 🔜 Single-stage amplifier
- 🔜 Two-stage OTA
- 🔜 Telescopic OTA
- 🔜 Folded-cascode OTA
- 🔜 Comparator
- 🔜 Bandgap reference
- 🔜 LDO regulator

---

## 🧠 AI Features

### **Parameter Optimization**
- Grid Search
- Random Search
- Particle Swarm Optimization (PSO)
- Genetic Algorithms
- Bayesian Optimization

### **Design Reasoning** (Future)
- Topology selection based on specs
- Constraint satisfaction
- Design rule checking
- Performance prediction

---

## 📊 Roadmap

### **Phase 1: Foundation** ✅ (Current)
- [x] Docker environment with Sky130 PDK
- [x] Ngspice, Magic, KLayout, Netgen integration
- [x] Sky130 device primitives
- [x] FastAPI backend skeleton
- [x] Basic circuit examples
- [x] Optimization engine foundation

### **Phase 2: Platform Development** 🔄 (In Progress)
- [ ] Complete API implementation
- [ ] Database integration
- [ ] Job queue system
- [ ] Layout automation scripts
- [ ] LVS verification automation

### **Phase 3: Circuit Library** 🔜 (Next)
- [ ] OpAmp variants
- [ ] Comparator designs
- [ ] Reference circuits
- [ ] Auto-sizing algorithms

### **Phase 4: AI Integration** 🔜 (Future)
- [ ] RL-based optimization
- [ ] LLM-augmented design
- [ ] Spec-to-circuit synthesis
- [ ] Performance prediction models

---

## 🤝 Contributing

We welcome contributions! This is a revolutionary platform that will change the IC design industry.

### **Priority Areas**
1. Sky130 circuit library expansion
2. Layout automation scripts
3. AI optimization algorithms
4. Test coverage
5. Documentation

---

## 📝 License

Apache 2.0 License - See LICENSE file

---

## 🙏 Acknowledgments

- **Google & SkyWater**: Sky130 open-source PDK
- **Tim Edwards**: Magic VLSI, Netgen, open_pdks
- **KLayout Community**: Layout automation tools
- **Ngspice Team**: SPICE simulation engine

---

## 📧 Contact

For questions, suggestions, or collaboration opportunities, please open an issue.

---

**Built with ❤️ for the future of analog IC design automation**
