"""Circuit API routes."""
from __future__ import annotations

import io
import json
import logging
import zipfile
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, StreamingResponse

from app.core.config import settings
from app.models.circuit import ProcessStatus, RunResponse, StatusResponse
from app.services.pipeline_executor import PipelineExecutor

logger = logging.getLogger(__name__)

router = APIRouter(prefix=settings.API_V1_PREFIX, tags=["circuits"])


def _work_dir() -> Path:
    path = Path(settings.WORK_DIR)
    path.mkdir(parents=True, exist_ok=True)
    return path


def _coerce_form_value(value):
    if not isinstance(value, str):
        return value

    stripped = value.strip()
    if not stripped:
        return value

    lowered = stripped.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False

    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        return value


async def _save_upload(file: UploadFile, process_id: str) -> Path:
    filename = Path(file.filename or "upload.py").name
    destination = _work_dir() / f"{process_id}_{filename}"

    contents = await file.read()
    with open(destination, "wb") as handle:
        handle.write(contents)

    return destination


def _get_process(process_id: str) -> dict:
    process = PipelineExecutor.processes.get(process_id)
    if not process:
        raise HTTPException(status_code=404, detail="Process not found")
    return process


def _process_error(process: dict) -> str | None:
    if process.get("error"):
        return process["error"]

    errors = process.get("errors") or []
    if not errors:
        return None

    return "; ".join(str(err) for err in errors)


def _serialize_results(request: Request, process_id: str, results: dict | None) -> dict | None:
    if not results:
        return results

    serialized = deepcopy(results)
    plot_paths = results.get("plots") or []

    plot_urls = [
        str(request.url_for("get_plot_artifact", process_id=process_id, plot_index=index))
        for index, _ in enumerate(plot_paths)
    ]
    serialized["plots"] = plot_urls

    raw_output = serialized.get("raw_output")
    if isinstance(raw_output, dict) and "plots" in raw_output:
        raw_output["plots"] = plot_urls

    return serialized


def _status_payload(request: Request, process_id: str, process: dict) -> StatusResponse:
    return StatusResponse(
        process_id=process_id,
        filename=process.get("filename"),
        status=process.get("status", ProcessStatus.PENDING),
        progress=process.get("progress", 0),
        parameters=process.get("parameters") or {},
        mode=process.get("mode", "simulate"),
        results=_serialize_results(request, process_id, process.get("results")),
        error=_process_error(process),
        created_at=process.get("created_at"),
        updated_at=process.get("updated_at"),
    )


@router.post("/run", response_model=RunResponse)
async def run_circuit(
    background_tasks: BackgroundTasks,
    request: Request,
    file: UploadFile = File(...),
):
    form = await request.form()

    mode = str(form.get("mode", "simulate")).strip().lower() or "simulate"
    parameters = {}

    raw_parameters = form.get("parameters")
    if raw_parameters:
        if not isinstance(raw_parameters, str):
            raise HTTPException(status_code=400, detail="`parameters` must be a JSON object string")
        try:
            parsed = json.loads(raw_parameters)
        except json.JSONDecodeError as exc:
            raise HTTPException(status_code=400, detail=f"Invalid parameters JSON: {exc.msg}") from exc
        if not isinstance(parsed, dict):
            raise HTTPException(status_code=400, detail="`parameters` must decode to a JSON object")
        parameters.update(parsed)

    for key, value in form.items():
        if key in {"file", "parameters", "mode"}:
            continue
        parameters[key] = _coerce_form_value(value)

    process_id = str(uuid4())
    saved_file = await _save_upload(file, process_id)
    now = datetime.utcnow()
    filename = Path(file.filename or saved_file.name).name

    PipelineExecutor.processes[process_id] = {
        "process_id": process_id,
        "filename": filename,
        "status": ProcessStatus.PENDING,
        "progress": 0,
        "parameters": parameters,
        "mode": mode,
        "results": None,
        "errors": [],
        "created_at": now,
        "updated_at": now,
        "file_path": str(saved_file),
    }

    background_tasks.add_task(
        PipelineExecutor.run_circuit_from_file,
        process_id,
        str(saved_file),
        parameters,
        mode,
    )

    return RunResponse(
        process_id=process_id,
        filename=filename,
        status=ProcessStatus.PENDING,
        parameters=parameters,
        mode=mode,
        message="Circuit submitted successfully",
    )


@router.get("/status/{process_id}", response_model=StatusResponse)
def get_status(process_id: str, request: Request):
    process = _get_process(process_id)
    return _status_payload(request, process_id, process)


@router.get("/plots/{process_id}/{plot_index}", name="get_plot_artifact")
def get_plot_artifact(process_id: str, plot_index: int):
    process = _get_process(process_id)
    results = process.get("results") or {}
    plot_paths = results.get("plots") or []

    if plot_index < 0 or plot_index >= len(plot_paths):
        raise HTTPException(status_code=404, detail="Plot not found")

    plot_path = Path(plot_paths[plot_index])
    if not plot_path.exists() or not plot_path.is_file():
        raise HTTPException(status_code=404, detail="Plot file not found")

    return FileResponse(plot_path)


@router.get("/download/{process_id}")
def download_results(process_id: str, request: Request):
    process = _get_process(process_id)
    status = process.get("status")
    results = process.get("results")

    if status != ProcessStatus.COMPLETED or not results:
        raise HTTPException(status_code=400, detail="Results are not ready for download")

    summary = _status_payload(request, process_id, process).model_dump(mode="json")

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("summary.json", json.dumps(summary, indent=2, default=str))

        netlists = results.get("netlists") or {}
        for path in netlists.values():
            candidate = Path(path)
            if candidate.exists():
                archive.write(candidate, arcname=candidate.name)

        for path in results.get("plots") or []:
            candidate = Path(path)
            if candidate.exists():
                archive.write(candidate, arcname=candidate.name)

        uploaded_file = process.get("file_path")
        if uploaded_file:
            candidate = Path(uploaded_file)
            if candidate.exists():
                archive.write(candidate, arcname=candidate.name)

    buffer.seek(0)
    headers = {
        "Content-Disposition": f'attachment; filename="{process_id}_results.zip"'
    }
    return StreamingResponse(buffer, media_type="application/zip", headers=headers)


@router.post("/introspect")
async def introspect_circuit(file: UploadFile = File(...)):
    process_id = f"introspect_{uuid4().hex}"
    saved_file = await _save_upload(file, process_id)
    parameters = PipelineExecutor.parse_parameters_from_file(str(saved_file))
    return {"parameters": parameters}
