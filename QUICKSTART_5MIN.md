# Quick Start — 5 Minutes to Your First Optimization

## Step 1: Verify Everything is Running (30 seconds)

```bash
# Check Docker container
docker ps | grep sky130_eda

# Check API health
curl http://localhost:8000/health
# Should return: {"status":"ok"}
```

✅ If both work, go to Step 2.  
❌ If failed, see [Troubleshooting](COMPLETE_SETUP_GUIDE.md#troubleshooting)

---

## Step 2: Open Swagger UI (10 seconds)

Open your browser and go to:

**http://localhost:8000/docs**

You'll see all API endpoints ready to test.

---

## Step 3: Create a Test Circuit File (1 minute)

Create file `my_circuit.py`:

```python
"""Simple current mirror circuit"""

PARAMETERS = {
    'iref': 10e-6,      # Reference current (A)
    'W': 2.0,           # Width (µm)
    'L': 0.5,           # Length (µm)
}
```

That's it! The system will auto-extract these parameters.

---

## Step 4: Upload Circuit (1 minute)

In Swagger UI:

1. Click **`POST /api/v1/upload`**
2. Click **"Try it out"**
3. Click **"Choose File"** → Select `my_circuit.py`
4. Click **"Execute"**
5. **Copy the `process_id`** (e.g., `proc_abc123xyz`)

---

## Step 5: View Extracted Parameters (30 seconds)

1. Click **`GET /api/v1/parameters/{process_id}`**
2. Click **"Try it out"**
3. Paste your `process_id`
4. Click **"Execute"**

You'll see:
```json
{
  "process_id": "proc_abc123xyz",
  "parameters": [
    {"name": "iref", "type": "float", "default": 1e-5},
    {"name": "W", "type": "float", "default": 2.0},
    {"name": "L", "type": "float", "default": 0.5}
  ]
}
```

---

## Step 6: Submit Parameters & Run Simulation (2 minutes)

1. Click **`POST /api/v1/submit/{process_id}`**
2. Click **"Try it out"**
3. Paste your `process_id`
4. Enter this in the request body:
   ```json
   {
     "iref": 1.5e-5,
     "W": 3.0,
     "L": 0.8
   }
   ```
5. Click **"Execute"**

Simulation starts in background! ✅

---

## Step 7: Check Results (1 minute)

1. Click **`GET /api/v1/status/{process_id}`**
2. Click **"Try it out"**
3. Paste your `process_id`
4. Click **"Execute"**

**Wait until `"progress": 100`**

Then view results:
```json
{
  "status": "completed",
  "progress": 100,
  "results": {
    "netlist_path": "data/designs/proc_abc123xyz.spice",
    "simulation_output": {
      "operating_point": {
        "id": 1.5e-05,
        "vgs": 0.65
      },
      "ac_analysis": {
        "gain_db": 42.5,
        "bandwidth_hz": 900000.0
      }
    }
  }
}
```

---

## Done! ✅

You've just:
- ✅ Uploaded a circuit file
- ✅ Automatically extracted parameters  
- ✅ Ran a simulation with custom values
- ✅ Got performance results (gain, bandwidth, etc.)

---

## Next: Try Optimization (Bonus — 2 minutes)

The same flow can use **AI-powered optimization** to find best parameters automatically.

**Instead of manually testing values**, use:

```python
# In Python code:
from ai_engine.optimizers.base_optimizer import OptimizationMethod, create_optimizer

optimizer = create_optimizer(OptimizationMethod.BAYESIAN_NN, ...)  # Smart!
# vs
optimizer = create_optimizer(OptimizationMethod.RANDOM_SEARCH, ...)  # Slow
```

**Bayesian = 3-5x faster** because it uses intelligence instead of random guessing.

See [Complete Guide](COMPLETE_SETUP_GUIDE.md#using-optimization) for how to integrate.

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `curl: (7) Failed to connect` | API not running. Run: `docker exec sky130_eda bash -c "cd /home/eda/backend && PYTHONPATH=/home/eda/backend python3 app/main.py &"` |
| `404 Not Found` on endpoints | Upload new files to container: `docker cp backend/app/api/circuits.py sky130_eda:/home/eda/backend/app/api/` |
| `Process not found` in status | Wait 5 seconds (simulation takes time). Status updates in background. |
| Python import errors | Run API with correct PYTHONPATH: `PYTHONPATH=/home/eda/backend python3 app/main.py` |

---

## Summary

```
5 minutes → Full analog circuit simulation via API
15 minutes → Understand entire system (read COMPLETE_SETUP_GUIDE.md)
30 minutes → Integrate with your own circuits
1 hour → Add custom optimizations
```

**You now have a professional EDA platform!** 🚀
