# Simplified API Flow - Single Endpoint

## Overview

**Old Flow:** Upload → Extract Parameters → Submit Parameters → Check Status (4 requests)

**New Flow:** Upload + Parameters Together → Check Status (2 requests, or 1 if you wait)

Much simpler and more user-friendly! ✨

---

## The Single Unified Endpoint

### `POST /api/v1/run`

**Upload circuit file + parameters in ONE request**

**Content-Type:** `multipart/form-data`

#### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file` | File | ✅ Yes | Python circuit file |
| `parameters` | String | ✅ Yes | JSON string with parameter values |

#### Example Request (curl)

```bash
curl -X POST http://localhost:8000/api/v1/run \
  -F "file=@circuit.py" \
  -F 'parameters={"w": 2.0, "l": 0.5, "iref": 10e-6}'
```

#### Example Response

```json
{
  "process_id": "proc_a1b2c3d4e5f6",
  "filename": "proc_a1b2c3d4e5f6_circuit.py",
  "status": "running",
  "parameters": {
    "w": 2.0,
    "l": 0.5,
    "iref": 0.00001
  },
  "message": "Circuit processing started. Check status with GET /status/{process_id}"
}
```

---

## Check Processing Status

### `GET /api/v1/status/{process_id}`

**Check if circuit is done and get results**

#### Example Request

```bash
curl http://localhost:8000/api/v1/status/proc_a1b2c3d4e5f6
```

#### While Running

```json
{
  "process_id": "proc_a1b2c3d4e5f6",
  "filename": "proc_a1b2c3d4e5f6_circuit.py",
  "status": "running",
  "progress": 45,
  "parameters": {
    "w": 2.0,
    "l": 0.5,
    "iref": 0.00001
  },
  "results": null,
  "error": null,
  "created_at": "2026-02-05T10:30:00",
  "updated_at": "2026-02-05T10:30:05"
}
```

#### When Complete

```json
{
  "process_id": "proc_a1b2c3d4e5f6",
  "filename": "proc_a1b2c3d4e5f6_circuit.py",
  "status": "completed",
  "progress": 100,
  "parameters": {
    "w": 2.0,
    "l": 0.5,
    "iref": 0.00001
  },
  "results": {
    "gain_db": 45.2,
    "bandwidth_hz": 1000000.0,
    "operating_point": {
      "vout": 0.95
    },
    "power_consumption": {
      "power_mw": 2.5
    }
  },
  "error": null,
  "created_at": "2026-02-05T10:30:00",
  "updated_at": "2026-02-05T10:30:08"
}
```

#### On Error

```json
{
  "process_id": "proc_a1b2c3d4e5f6",
  "filename": "proc_a1b2c3d4e5f6_circuit.py",
  "status": "failed",
  "progress": 0,
  "parameters": {
    "w": 2.0,
    "l": 0.5,
    "iref": 0.00001
  },
  "results": null,
  "error": "Circuit simulation failed: Missing required parameter 'length'",
  "created_at": "2026-02-05T10:30:00",
  "updated_at": "2026-02-05T10:30:02"
}
```

---

## Complete Example Workflow

### Step 1: Run Circuit (with file + parameters)

```bash
curl -X POST http://localhost:8000/api/v1/run \
  -F "file=@circuits/generators/demo_master.py" \
  -F 'parameters={"w": 2.0, "l": 0.5, "iref": 10e-6}'
```

**Response:** `process_id = proc_a1b2c3d4e5f6`

### Step 2: Check Status

```bash
curl http://localhost:8000/api/v1/status/proc_a1b2c3d4e5f6
```

**Response:** See examples above

### Step 3: When Completed, Extract Results

```bash
curl http://localhost:8000/api/v1/status/proc_a1b2c3d4e5f6 | jq '.results'
```

**Output:**
```json
{
  "gain_db": 45.2,
  "bandwidth_hz": 1000000.0,
  "operating_point": {
    "vout": 0.95
  },
  "power_consumption": {
    "power_mw": 2.5
  }
}
```

---

## Using Swagger UI

### 1. Open Swagger UI

```
http://localhost:8000/docs
```

### 2. Find "circuits" section

Look for **POST /api/v1/run** endpoint

### 3. Click "Try it out"

### 4. Fill in:
- **file:** Upload your circuit file (e.g., `demo_master.py`)
- **parameters:** Paste JSON (e.g., `{"w": 2.0, "l": 0.5, "iref": 10e-6}`)

### 5. Click "Execute"

### 6. Get process_id from response

### 7. Use GET /api/v1/status/{process_id} to check results

---

## Parameter Format

Parameters MUST be valid JSON:

✅ **Correct:**
```json
{"w": 2.0, "l": 0.5, "iref": 10e-6}
```

❌ **Wrong:**
```
w: 2.0, l: 0.5, iref: 10e-6
```

When using curl with `-F`, wrap the entire JSON in single quotes:

```bash
-F 'parameters={"w": 2.0, "l": 0.5}'
```

---

## Python Example

```python
import requests
import json
import time

# 1. Run circuit
with open("circuits/generators/demo_master.py", "rb") as f:
    files = {"file": f}
    data = {"parameters": json.dumps({"w": 2.0, "l": 0.5, "iref": 10e-6})}
    response = requests.post("http://localhost:8000/api/v1/run", files=files, data=data)
    
process_id = response.json()["process_id"]
print(f"Started: {process_id}")

# 2. Poll for results
while True:
    status = requests.get(f"http://localhost:8000/api/v1/status/{process_id}").json()
    
    if status["status"] == "completed":
        print("✅ Done!")
        print(f"Results: {status['results']}")
        break
    elif status["status"] == "failed":
        print(f"❌ Error: {status['error']}")
        break
    else:
        print(f"⏳ Progress: {status['progress']}%")
        time.sleep(1)
```

---

## Common Issues

### "Invalid JSON in parameters"
Make sure your JSON is valid. Use a JSON validator or tool.

### "Process not found"
The process_id might be expired or wrong. Check the id from the /run response.

### "File not found"
Make sure the file path is correct and the file was uploaded successfully.

---

## Summary

| Step | Method | Endpoint | Purpose |
|------|--------|----------|---------|
| 1 | POST | `/api/v1/run` | Upload file + parameters together |
| 2 | GET | `/api/v1/status/{id}` | Check status and get results |

**That's it!** Two endpoints, one flow. Much simpler. 🚀
