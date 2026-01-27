# 🚀 Getting Started Guide

## Step-by-Step Setup

### 1. **Build the Enhanced Docker Image**

The new Dockerfile includes the full Sky130 PDK and EDA stack. This will take significant time on first build.

```bash
cd /home/user/analog-eda/docker
docker-compose build eda-platform
```

**Expected build time**: 30-60 minutes depending on your system

**What's being installed**:
- Sky130 PDK (open_pdks) - Downloads ~2GB
- Magic VLSI - Compiled from source
- KLayout - Compiled with Python bindings
- Netgen - LVS tool
- All Python dependencies

### 2. **Start the Platform**

```bash
docker-compose up -d
```

This starts:
- `sky130_eda` - Main EDA container
- `redis` - For task queue
- `postgres` - Database (optional)

### 3. **Enter the Container**

```bash
docker exec -it sky130_eda bash
```

You should see:
```
╔════════════════════════════════════════════════════╗
║  AI-Driven Sky130 ASIC Platform                   ║
║  PDK: Sky130A | Tools: Magic, KLayout, Netgen     ║
╚════════════════════════════════════════════════════╝
```

### 4. **Verify Installation**

Inside the container:

```bash
# Check Ngspice
ngspice --version

# Check Sky130 PDK
ls /opt/sky130_pdk/sky130A

# Check Magic
magic -noconsole --version

# Check Python environment
python3 -c "from circuits.sky130.devices import nmos; print('Sky130 library OK')"
```

### 5. **Run First Sky130 Circuit**

```bash
cd /home/eda/circuits/library
python3 rc_sky130_example.py
```

This generates a SPICE netlist with real Sky130 models.

```bash
ngspice sky130_rc.spice
```

You should see simulation results with time constant measurements!

### 6. **Run Current Mirror Example**

```bash
cd /home/eda/circuits/library/current_mirror
python3 sky130_current_mirror.py
ngspice sky130_current_mirror.spice
```

This demonstrates:
- Sky130 NMOS transistor usage
- Operating point analysis
- Current measurement
- Output resistance calculation

### 7. **Start FastAPI Backend**

```bash
cd /home/eda/backend
python3 -m app.main
```

Access the API at: `http://localhost:8000`

API documentation: `http://localhost:8000/docs`

### 8. **Test Optimization Engine**

```bash
cd /home/eda/ai_engine/optimizers
python3 -c "
from base_optimizer import *
import numpy as np

# Define parameter space
params = [
    ParameterSpace('x', -10, 10),
    ParameterSpace('y', -10, 10)
]

# Simple objective: minimize (x-3)^2 + (y+2)^2
objectives = [
    ObjectiveSpec('result', target=0, minimize=True)
]

# Test function
def obj_func(p):
    return {'result': (p['x']-3)**2 + (p['y']+2)**2}

# Optimize
opt = create_optimizer(
    OptimizationMethod.PARTICLE_SWARM,
    params,
    objectives,
    max_iterations=50
)

result = opt.optimize(obj_func)
print(f'Best parameters: {result.best_parameters}')
print(f'Best score: {result.best_score}')
"
```

Expected output should show x ≈ 3, y ≈ -2

---

## Common Tasks

### **Create a New Circuit**

1. Create Python file in `/home/eda/circuits/library/<circuit_name>/`
2. Import Sky130 devices: `from circuits.sky130.devices import nmos, pmos, resistor, capacitor`
3. Implement circuit class with `generate_netlist()` method
4. Use Sky130 constants: `from circuits.sky130.devices import Sky130Constants`

### **Run Simulation**

```python
from tools.simulation.ngspice_wrapper import NgspiceSimulator

sim = NgspiceSimulator()
result = sim.simulate("path/to/netlist.spice")

if result.success:
    print(f"Measurements: {result.measurements}")
    data = sim.load_csv_data(result.data_file)
```

### **Optimize Circuit Parameters**

```python
from ai_engine.optimizers.base_optimizer import *

# Define what to optimize
params = [
    ParameterSpace(name="width", min_value=1.0, max_value=10.0),
    ParameterSpace(name="length", min_value=0.5, max_value=2.0),
]

# Define targets
objectives = [
    ObjectiveSpec(name="gain", target=40, weight=1.0),  # 40dB gain
    ObjectiveSpec(name="bandwidth", target=1e6, weight=0.5),  # 1MHz
]

# Define objective function (runs simulation)
def evaluate(params):
    # Generate circuit with params
    # Run simulation
    # Return performance metrics
    return {"gain": ..., "bandwidth": ...}

# Optimize
optimizer = create_optimizer(
    method=OptimizationMethod.PARTICLE_SWARM,
    parameter_spaces=params,
    objectives=objectives,
    max_iterations=100
)

result = optimizer.optimize(evaluate)
print(f"Optimal: {result.best_parameters}")
```

---

## Troubleshooting

### **Docker build fails**

- Check disk space (need ~10GB free)
- Check internet connection (downloads ~3GB)
- Try building without cache: `docker-compose build --no-cache`

### **Sky130 PDK not found**

Inside container:
```bash
ls /opt/sky130_pdk/sky130A
```

If missing, the PDK installation failed. Check build logs.

### **Ngspice simulation fails**

- Check netlist syntax
- Verify Sky130 model library path: `/opt/sky130_pdk/sky130A/libs.tech/ngspice/sky130.lib.spice`
- Check simulation log file for errors

### **Python import errors**

```bash
export PYTHONPATH=/home/eda:$PYTHONPATH
```

Add to `~/.bashrc` for persistence.

---

## Next Steps

1. **Explore existing circuits** in `/home/eda/circuits/library/`
2. **Build your first OpAmp** using Sky130 transistors
3. **Set up layout automation** with Magic
4. **Implement LVS verification** workflow
5. **Train AI models** on your design data

---

## Development Workflow

```
1. Design Circuit (Python + Sky130 devices)
        ↓
2. Generate Netlist (.spice)
        ↓
3. Simulate (Ngspice)
        ↓
4. Analyze Results
        ↓
5. Optimize Parameters (AI Engine)
        ↓
6. Generate Layout (Magic)
        ↓
7. Verify LVS (Netgen)
        ↓
8. Extract Parasitics
        ↓
9. Post-layout Simulation
        ↓
10. Tape-out Ready! 🎉
```

---

**Happy Designing! 🚀**
