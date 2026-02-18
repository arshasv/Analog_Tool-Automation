"""Circuit API: Upload, Run, Status, Download (SPICE netlist + PNG)"""
import uuid
import os
import io
import json
import logging
import zipfile
import glob
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from fastapi import APIRouter, HTTPException, BackgroundTasks, UploadFile, File, Form
from fastapi.responses import StreamingResponse

from app.models.circuit import RunResponse, StatusResponse, ProcessStatus
from app.services.pipeline_executor import PipelineExecutor

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["circuits"])




@router.post("/run", response_model=RunResponse)
async def run_circuit(
    file: UploadFile = File(...),
    parameters: Optional[str] = Form(None),
    background_tasks: BackgroundTasks = None,
):
    """Upload circuit .py file and optional JSON parameters. Returns process_id."""
    user_params = {}
    if parameters:
        try:
            user_params = json.loads(parameters)
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=400, detail=f"Invalid JSON: {e}")

    process_id = f"proc_{uuid.uuid4().hex[:12]}"
    work_dir = Path("data/designs")
    uploads_dir = work_dir / "uploads"
    uploads_dir.mkdir(parents=True, exist_ok=True)
    
    filename = f"{process_id}_{file.filename}"
    file_path = str(uploads_dir / filename)

    content = await file.read()
    with open(file_path, "wb") as fh:
        fh.write(content)

    # Initialise process state
    PipelineExecutor.processes[process_id] = {
        "process_id": process_id,
        "status": ProcessStatus.RUNNING,
        "progress": 0,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "results": None,
        "errors": [],
        "file_path": file_path,
        "filename": file.filename,
        "provided_parameters": user_params,
    }

    # Schedule background execution
    if background_tasks is not None:
        background_tasks.add_task(
            PipelineExecutor.run_circuit_from_file,
            process_id, file_path, user_params,
        )
    else:
        import asyncio
        asyncio.create_task(
            asyncio.to_thread(
                PipelineExecutor.run_circuit_from_file,
                process_id, file_path, user_params,
            )
        )

    return RunResponse(
        process_id=process_id,
        filename=file.filename,
        status=ProcessStatus.RUNNING,
        parameters=user_params,
        message="Circuit processing started.",
    )


@router.get("/status/{process_id}", response_model=StatusResponse)
async def get_status(process_id: str):
    """Check processing status and retrieve results."""
    if process_id not in PipelineExecutor.processes:
        raise HTTPException(status_code=404, detail="Process not found")

    proc = PipelineExecutor.processes[process_id]
    return StatusResponse(
        process_id=process_id,
        filename=proc.get("filename", "unknown"),
        status=proc["status"],
        progress=proc.get("progress", 0),
        parameters=proc.get("provided_parameters"),
        created_at=proc["created_at"],
        updated_at=proc.get("updated_at", proc["created_at"]),
        results=proc.get("results"),
        error="; ".join(proc.get("errors", [])) or None,
    )


@router.get("/download/{process_id}")
async def download_results(process_id: str):
    """Download ZIP containing .spice netlist and .png result plot"""
    if process_id not in PipelineExecutor.processes:
        raise HTTPException(status_code=404, detail="Process not found")

    proc = PipelineExecutor.processes[process_id]
    results = proc.get("results") or {}
    work_dir = Path("data/designs")
    
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        # 1. SPICE Netlists
        netlists = results.get("netlists", {})
        found_netlist = False
        
        for name, path_val in netlists.items():
            if name == "sequence": continue
            path = Path(path_val)
            # Try to find the file
            if path.exists():
                zf.write(str(path), arcname=f"{process_id}_{name}.spice")
                found_netlist = True
            elif (work_dir / path.name).exists():
                zf.write(str(work_dir / path.name), arcname=f"{process_id}_{name}.spice")
                found_netlist = True
        
        # Fallback: glob for any spice files with this process_id in work_dir
        if not found_netlist:
            for f in work_dir.glob(f"{process_id}*.spice"):
                zf.write(str(f), arcname=os.path.basename(f))
                found_netlist = True

        # 2. PNG Plots
        plots = results.get("plots", [])
        if not plots:
            # Fallback: check raw_output if pipeline executor didn't lift it (though we updated it)
            raw = results.get("raw_output", {})
            plots = raw.get("plots", [])

        for plot_path in plots:
            p = Path(plot_path)
            # Calculate archive name (just filename)
            arcname = p.name
            
            if p.exists():
                zf.write(str(p), arcname=arcname)
            elif (work_dir / p.name).exists():
                zf.write(str(work_dir / p.name), arcname=arcname)
            else:
                logger.warning(f"Plot file listed but not found: {plot_path}")

        # 3. Always include original source as fallback
        uploaded = proc.get("file_path", "")
        if uploaded and os.path.exists(uploaded):
            zf.write(uploaded, arcname=f"source_{process_id}.py")

        # 4. Summary JSON
        summary = {
            "metrics": results.get("metrics"),
            "score": results.get("score"),
            "checks": results.get("checks"),
            "status": proc["status"],
            "errors": proc.get("errors", [])
        }
        zf.writestr(f"summary_{process_id}.json", json.dumps(summary, indent=2))

    buf.seek(0)
    return StreamingResponse(
        buf, 
        media_type="application/zip", 
        headers={"Content-Disposition": f"attachment; filename=results_{process_id}.zip"}
    )
