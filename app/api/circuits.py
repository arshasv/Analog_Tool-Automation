"""Circuit API: Simple unified single-endpoint flow - upload file and optional parameters"""
import uuid
import os
from datetime import datetime
from fastapi import APIRouter, HTTPException, BackgroundTasks, UploadFile, File, Form
from typing import Dict, Any, Optional
import json
from app.models.circuit import (
    CircuitRequest,
    ProcessState,
    ProcessStatus,
    RunResponse,
    StatusResponse,
)
from app.services.pipeline_executor import PipelineExecutor
from fastapi.responses import StreamingResponse
import io
import zipfile
from app.utils.plotting import plot_simulation_output_png

router = APIRouter(prefix="/api/v1", tags=["circuits"])


@router.get("/debug/processes")
async def debug_list_processes():
    """Debug endpoint: list known process ids in memory (for dev only)."""
    return {"processes": list(PipelineExecutor.processes.keys())}


@router.post("/run", response_model=RunResponse)
async def run_circuit(
    file: UploadFile = File(...),
    parameters: Optional[str] = Form(None),
    background_tasks: BackgroundTasks = None,
):
    """
    Upload circuit file with optional parameters.
    
    Request (multipart/form-data):
      - file: Python circuit file (required)
      - parameters: JSON string with parameter values (optional)
        If not provided, uses defaults from Python file's PARAMETERS dict or function signature.
        If provided, overrides the file's defaults.
    
    Example with parameters:
      curl -X POST http://localhost:8000/api/v1/run \\
        -F "file=@circuit.py" \\
        -F "parameters={\\"w\\": 2.0, \\"l\\": 0.5}"
    
    Example without parameters (uses file's defaults):
      curl -X POST http://localhost:8000/api/v1/run \\
        -F "file=@circuit.py"
    
    Returns immediately with process_id and status. Use GET /status/{process_id} to check results.
    """
    # Parse parameters JSON if provided
    user_params = {}
    if parameters:
        try:
            user_params = json.loads(parameters)
            if not isinstance(user_params, dict):
                raise ValueError("Parameters must be a JSON object")
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=400, detail=f"Invalid JSON in parameters: {str(e)}")
    
    # Save uploaded file
    process_id = f"proc_{uuid.uuid4().hex[:12]}"
    uploads_dir = os.path.join("data", "designs", "uploads")
    os.makedirs(uploads_dir, exist_ok=True)
    filename = f"{process_id}_{file.filename}"
    file_path = os.path.join(uploads_dir, filename)
    
    with open(file_path, "wb") as fh:
        fh.write(await file.read())
    
    # Extract defaults from file and merge with user-provided parameters
    file_params = PipelineExecutor.parse_parameters_from_file(file_path)
    final_params = {}
    
    # First, use defaults from file
    for param_spec in file_params:
        if param_spec.get("default") is not None:
            final_params[param_spec["name"]] = param_spec["default"]
    
    # Then override with user-provided parameters
    final_params.update(user_params)
    
    # Initialize process state
    PipelineExecutor.processes[process_id] = {
        "process_id": process_id,
        "status": ProcessStatus.RUNNING,
        "progress": 0,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "results": None,
        "error": None,
        "file_path": file_path,
        "filename": filename,
        "provided_parameters": final_params,
    }
    
    # Schedule background execution with merged parameters
    if background_tasks is not None:
        background_tasks.add_task(PipelineExecutor.run_circuit_from_file, process_id, file_path, final_params)
    else:
        import asyncio
        asyncio.create_task(PipelineExecutor.run_circuit_from_file(process_id, file_path, final_params))
    
    return RunResponse(
        process_id=process_id,
        filename=filename,
        status=ProcessStatus.RUNNING,
        parameters=final_params,
        message="Circuit processing started. Check status with GET /status/{process_id}"
    )


@router.get("/status/{process_id}", response_model=StatusResponse)
async def get_status(process_id: str):
    """Check circuit processing status and get results when ready"""
    
    if process_id not in PipelineExecutor.processes:
        raise HTTPException(status_code=404, detail="Process not found")
    
    proc = PipelineExecutor.processes[process_id]
    
    return StatusResponse(
        process_id=process_id,
        filename=proc.get("filename"),
        status=proc["status"],
        progress=proc["progress"],
        parameters=proc.get("provided_parameters"),
        created_at=proc["created_at"],
        updated_at=proc["updated_at"],
        results=proc.get("results"),
        error=proc.get("error")
    )


@router.get("/download/{process_id}")
async def download_results_zip(process_id: str):
    """Return a ZIP file containing the netlist (.spice) and a PNG plot of results.

    The ZIP is created in-memory and streamed to the caller.
    """
    if process_id not in PipelineExecutor.processes:
        raise HTTPException(status_code=404, detail="Process not found")

    proc = PipelineExecutor.processes[process_id]
    results = proc.get("results") or {}
    sim = results.get("simulation_output") or {}
    netlist_paths = results.get("netlist_paths") or {}

    # Choose primary netlist (dc) if present
    netlist_file = netlist_paths.get("dc") or netlist_paths.get("primary_netlist")
    # If netlist not available, fallback to uploaded source file
    uploaded_file = proc.get("file_path")
    if not netlist_file or not os.path.exists(netlist_file):
        # If a netlist file isn't present on disk, attempt to use the uploaded
        # source. If that also isn't present, fall back to embedding the
        # simulation_output JSON into the ZIP so the user still receives useful
        # information and the PNG plot.
        if uploaded_file and os.path.exists(uploaded_file):
            use_uploaded = True
            attach_path = uploaded_file
        else:
            use_uploaded = False
            attach_path = None
    else:
        use_uploaded = False
        attach_path = netlist_file

    # Generate PNG plot bytes from simulation output
    try:
        png_bytes = plot_simulation_output_png(sim)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Plot generation failed: {e}")

    # Create in-memory ZIP
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        # Add netlist file (or uploaded source) preserving name if available
        if attach_path:
            try:
                zf.write(attach_path, arcname=os.path.basename(attach_path))
            except Exception:
                with open(attach_path, 'rb') as nf:
                    zf.writestr(os.path.basename(attach_path), nf.read())
        else:
            # No netlist available on disk; include simulation_output JSON instead
            import json as _json
            zf.writestr(f"{process_id}_simulation_output.json", _json.dumps(sim, indent=2))

        # Add PNG plot
        zf.writestr(f"{process_id}_result.png", png_bytes)

    buf.seek(0)

    headers = {
        "Content-Disposition": f"attachment; filename=results_{process_id}.zip"
    }
    return StreamingResponse(buf, media_type="application/zip", headers=headers)
