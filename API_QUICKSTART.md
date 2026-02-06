# ⚡ Quick Start - Simplified API (2 Steps)

## What Changed?

**Before:** Upload → Extract Params → Submit → Check Status (4 requests)  
**Now:** Upload + Parameters → Check Status (2 requests) ✨

## Single Endpoint

### `POST /api/v1/run` 

Upload your Python circuit file **AND** parameter values in **ONE request**.

---

## Quick Example

### Step 1: Send File + Parameters

```bash
curl -X POST http://localhost:8000/api/v1/run \
  -F "file=@circuit.py" \
  -F 'parameters={"w": 2.0, "l": 0.5, "iref": 10e-6}'
```

**Get back:**
```json
{
  "process_id": "proc_a1b2c3d4",
  "status": "running",
  "parameters": {"w": 2.0, "l": 0.5, "iref": 10e-6},
  "message": "Check status with GET /status/{process_id}"
}
```

### Step 2: Check Results

```bash
curl http://localhost:8000/api/v1/status/proc_a1b2c3d4
```

**Get back (when done):**
```json
{
  "process_id": "proc_a1b2c3d4",
  "status": "completed",
  "results": {
    "gain_db": 42.0,
    "bandwidth_hz": 900000.0,
    "operating_point": {"vdd": 1.8}
  }
}
```

---

## Using Swagger UI (GUI)

### 1. Open http://localhost:8000/docs

### 2. Click on **POST /api/v1/run**

### 3. Click "Try it out"

### 4. Fill in:
- **file:** Upload your circuit file
- **parameters:** Paste JSON (e.g., `{"w": 2.0, "l": 0.5, "iref": 10e-6}`)

### 5. Click "Execute" → Get process_id

### 6. Then use **GET /api/v1/status/{process_id}** to check results

---

## Python Example

```python
import requests
import json
import time

# Step 1: Upload + Run
with open("my_circuit.py", "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/v1/run",
        files={"file": f},
        data={"parameters": json.dumps({"w": 2.0, "l": 0.5, "iref": 10e-6})}
    )

process_id = response.json()["process_id"]
print(f"Running: {process_id}")

# Step 2: Poll for results
while True:
    status = requests.get(f"http://localhost:8000/api/v1/status/{process_id}").json()
    
    if status["status"] == "completed":
        print("✅ Done!")
        print(f"Gain: {status['results']['simulation_output']['ac_analysis']['gain_db']} dB")
        break
    elif status["status"] == "failed":
        print(f"❌ Error: {status['error']}")
        break
    else:
        print(f"⏳ Still running...")
        time.sleep(1)
```

---

## Parameters Format

Your `parameters` must be valid JSON:

```json
{"w": 2.0, "l": 0.5, "iref": 10e-6}
```

When using `curl -F`, wrap in single quotes:
```bash
-F 'parameters={"w": 2.0, "l": 0.5}'
```

---

## Status Codes

| Status | Meaning | Action |
|--------|---------|--------|
| `running` | Still processing | Wait and poll again |
| `completed` | ✅ Done! | Check `results` |
| `failed` | ❌ Error | Check `error` field |

---

## Two Endpoints, That's It!

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/v1/run` | Upload file + params → start simulation |
| GET | `/api/v1/status/{process_id}` | Check status and get results |

**Simple. Clean. Fast.** 🚀
