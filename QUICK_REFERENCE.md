# ⚡ Quick Reference Card

## 🚀 Essential Commands

```bash
# Build platform
make build              # Initial build (30-60 min)

# Start/stop
make up                 # Start all services
make down               # Stop all services
make restart            # Restart services

# Access
make shell              # Enter container
make logs               # View logs
make backend            # Start FastAPI

# Examples
make simulate           # Run example circuits
make check              # Verify installation
```

---

## 🔧 Inside Container

```bash
# Verify tools
ngspice --version
magic -noconsole --version
ls /opt/sky130_pdk/sky130A

# Run examples
cd /home/eda/circuits/library
python3 rc_sky130_example.py
ngspice sky130_rc.spice

# Start backend
cd /home/eda/backend
python3 -m app.main
```

---

## 📝 Python Quick Start

```python
# 1. Import Sky130 devices
from circuits.sky130.devices import nmos, pmos, resistor, capacitor

# 2. Create devices
m1 = nmos("M1", width=2.0, length=0.5, nf=1)
r1 = resistor("R1", resistance=10e3)
c1 = capacitor("C1", capacitance=10e-12)

# 3. Generate SPICE
spice_line = m1.to_spice("drain", "gate", "source", "body")

# 4. Simulate
from tools.simulation.ngspice_wrapper import NgspiceSimulator
sim = NgspiceSimulator()
result = sim.simulate("netlist.spice")

# 5. Optimize
from ai_engine.optimizers.base_optimizer import *

params = [ParameterSpace("W", 1.0, 10.0)]
objectives = [ObjectiveSpec("gain", target=10)]
optimizer = create_optimizer(
    OptimizationMethod.PARTICLE_SWARM,
    params, objectives, max_iterations=50
)
result = optimizer.optimize(eval_func)
```

---

## 🎯 API Endpoints

```
GET  /                      # Platform info
GET  /health                # Health check
GET  /api/v1/info          # Detailed info
GET  /docs                  # Swagger UI
```

---

## 📊 Project Structure

```
analog-eda/
├── backend/            # FastAPI server
├── circuits/           # Circuit library
│   ├── sky130/        # PDK devices
│   ├── library/       # Circuit templates
│   └── generators/    # Base classes
├── ai_engine/          # Optimization
├── tools/              # EDA wrappers
├── docker/             # Containers
└── data/               # Results
```

---

## 🔍 File Locations

| Component | Location |
|-----------|----------|
| Sky130 Devices | `circuits/sky130/devices.py` |
| Circuit Examples | `circuits/library/` |
| Ngspice Wrapper | `tools/simulation/ngspice_wrapper.py` |
| Optimizers | `ai_engine/optimizers/` |
| FastAPI App | `backend/app/main.py` |
| Configuration | `backend/app/core/config.py` |

---

## 📚 Documentation

- `README.md` - Project overview
- `GETTING_STARTED.md` - Setup guide
- `STATUS.md` - Current status
- `IMPLEMENTATION_PLAN.md` - Roadmap

---

## 🐛 Troubleshooting

**Docker build fails?**
- Check disk space (need 10GB)
- Try: `docker-compose build --no-cache`

**PDK not found?**
- Inside container: `ls /opt/sky130_pdk/sky130A`

**Simulation fails?**
- Check netlist: `.lib /opt/sky130_pdk/sky130A/libs.tech/ngspice/sky130.lib.spice tt`

**Import errors?**
- `export PYTHONPATH=/home/eda:$PYTHONPATH`

---

## 💡 Tips

1. **Use Makefile** - Simplifies common tasks
2. **Check STATUS.md** - Current implementation status
3. **Read examples** - Best way to learn the API
4. **Start simple** - RC circuit → Current mirror → OpAmp
5. **Use optimization** - Let AI size your circuits

---

## 🎓 Key Concepts

**Sky130 Device Types:**
- `nmos()` - NMOS transistor
- `pmos()` - PMOS transistor
- `resistor()` - Poly resistor
- `capacitor()` - MIM capacitor

**Optimization Methods:**
- `GRID_SEARCH` - Exhaustive
- `RANDOM_SEARCH` - Fast exploration
- `PARTICLE_SWARM` - Good for analog
- `GENETIC_ALGORITHM` - Multi-objective

**Analysis Types:**
- `.op` - Operating point
- `.dc` - DC sweep
- `.ac` - AC analysis
- `.tran` - Transient

---

**🚀 Ready? Start with:** `make quickstart`
