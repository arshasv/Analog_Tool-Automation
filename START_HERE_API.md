# 🚀 START HERE: Simplified API

## What Just Changed?

Your API is now **much simpler**:

| | Before | After |
|---|--------|-------|
| **Endpoints** | 4 (upload, params, submit, status) | 2 (run, status) |
| **Steps to start** | 3 | 1 |
| **Requests needed** | 4 | 2 |
| **Complexity** | High ❌ | Low ✅ |

---

## The New Flow (Super Simple)

### Step 1: Upload File + Parameters (ONE Request)

```bash
curl -X POST http://localhost:8000/api/v1/run \
  -F "file=@my_circuit.py" \
  -F 'parameters={"w": 2.0, "l": 0.5, "iref": 10e-6}'
```

**Response:**
```json
{
  "process_id": "proc_abc123",
  "status": "running"
}
```

### Step 2: Check Status (Poll Until Done)

```bash
curl http://localhost:8000/api/v1/status/proc_abc123
```

**Response (when done):**
```json
{
  "status": "completed",
  "results": {
    "gain_db": 42.0,
    "bandwidth_hz": 900000
  }
}
```

**Done!** That's all you need. 2 requests, 2 endpoints. 🎉

---

## Use Swagger UI (GUI)

Don't like curl? Use the web interface:

1. Open http://localhost:8000/docs
2. Find **POST /api/v1/run**
3. Click "Try it out"
4. Upload file + parameters
5. Get process_id
6. Use **GET /api/v1/status/{id}** to check results

---

## Parameters Format

Your parameters must be **valid JSON**:

```json
{"w": 2.0, "l": 0.5, "iref": 10e-6}
```

Common mistakes to avoid:
```
❌ {"w": 2.0, "l": 0.5}  with extra comma
❌ {w: 2.0, l: 0.5}       without quotes
❌ w=2.0, l=0.5           not JSON format
```

When using curl with `-F`, wrap in single quotes:
```bash
-F 'parameters={"w": 2.0}'
```

---

## Python Example

```python
import requests
import json
import time

# 1. Upload + Run
with open("circuit.py", "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/v1/run",
        files={"file": f},
        data={"parameters": json.dumps({"w": 2.0, "l": 0.5, "iref": 10e-6})}
    )

process_id = response.json()["process_id"]
print(f"Process: {process_id}")

# 2. Poll for results
while True:
    status = requests.get(f"http://localhost:8000/api/v1/status/{process_id}").json()
    
    if status["status"] == "completed":
        print(f"✅ Done! Gain = {status['results']['simulation_output']['ac_analysis']['gain_db']} dB")
        break
    elif status["status"] == "failed":
        print(f"❌ Error: {status['error']}")
        break
    else:
        print(f"⏳ Running ({status['progress']}%)")
        time.sleep(1)
```

---

## Status Values

Your status will change as the circuit processes:

| Status | Meaning | Next Action |
|--------|---------|-------------|
| `running` | Still processing | Wait 1-2 seconds, ask again |
| `completed` | ✅ Done! | Read the `results` field |
| `failed` | ❌ Error occurred | Check the `error` field |

---

## Real Example Output

```bash
$ curl -s -X POST http://localhost:8000/api/v1/run \
  -F "file=@test_circuit.py" \
  -F 'parameters={"w": 3.0, "l": 1.0, "iref": 15e-6}' | jq .

{
  "process_id": "proc_a6f7a381e071",
  "filename": "proc_a6f7a381e071_test_circuit.py",
  "status": "running",
  "parameters": {
    "w": 3.0,
    "l": 1.0,
    "iref": 0.000015
  },
  "message": "Circuit processing started. Check status with GET /status/proc_a6f7a381e071"
}

$ curl -s http://localhost:8000/api/v1/status/proc_a6f7a381e071 | jq .results

{
  "netlist_path": "data/designs/proc_a6f7a381e071.spice",
  "simulation_output": {
    "operating_point": {
      "vdd": 1.8,
      "id": 0.000015
    },
    "ac_analysis": {
      "gain_db": 42.0,
      "bandwidth_hz": 900000.0
    }
  }
}
```

---

## Documentation

Read these files for more details:

| File | Purpose | Time |
|------|---------|------|
| [API_QUICKSTART.md](API_QUICKSTART.md) | This file! | 5 min |
| [SIMPLIFIED_API_FLOW.md](SIMPLIFIED_API_FLOW.md) | Complete API reference | 10 min |
| [BEFORE_AFTER_COMPARISON.md](BEFORE_AFTER_COMPARISON.md) | Why it's better | 5 min |
| [SIMPLIFIED_API_SUMMARY.txt](SIMPLIFIED_API_SUMMARY.txt) | Quick overview | 3 min |

---

## Common Questions

### Q: Can I provide parameters in the URL?
**A:** No, parameters must be in the `parameters` form field as JSON.

### Q: How long does a circuit take to run?
**A:** Usually 2-5 seconds. Check status to see progress.

### Q: Can I upload multiple files?
**A:** One file per request. Run multiple requests for multiple circuits.

### Q: What if parameters are wrong?
**A:** The status will be `failed` with an error message. Check the `error` field.

### Q: Can I download the results?
**A:** Results are returned in the status response as JSON. The netlist is saved to `data/designs/` if you need it.

---

## Quick Reference

**Upload + Run:**
```bash
curl -X POST http://localhost:8000/api/v1/run \
  -F "file=@circuit.py" \
  -F 'parameters={"w": 2.0, "l": 0.5, "iref": 10e-6}'
```

**Check Status:**
```bash
curl http://localhost:8000/api/v1/status/{process_id}
```

**Swagger UI:**
```
http://localhost:8000/docs
```

---

## Summary

**Old way:** Upload → Extract params → Submit → Check (confusing, 4 steps)  
**New way:** Upload + params → Check (simple, 2 steps)

**Benefits:**
- ✅ Simpler to understand
- ✅ Faster to execute
- ✅ Cleaner responses
- ✅ More intuitive
- ✅ Better documentation

**Status:** Fully working and tested ✅

**Next:** Try it yourself! Pick a circuit and upload it now! 🚀
