#!/usr/bin/env bash

set -euo pipefail

# Create work directories
mkdir -p /work/input /work/output /work/logs

# Launch uvicorn
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1
