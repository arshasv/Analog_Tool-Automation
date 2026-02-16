"""
Unit tests for the current_mirror circuit: netlist generation and pipeline run.
"""
import os
import sys
from pathlib import Path

import pytest

# Project root
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def test_current_mirror_generate_netlist():
    """Current mirror generate_netlist() returns a valid SPICE netlist."""
    from app.circuits.current_mirror import generate_netlist

    netlist = generate_netlist(width=2.0, length=0.5)
    assert isinstance(netlist, str)
    assert len(netlist) > 0
    assert "Sky130 Current Mirror" in netlist
    assert "sky130.lib.spice" in netlist
    assert "sky130_fd_pr__nfet_01v8" in netlist
    assert "XM1" in netlist and "XM2" in netlist
    assert "vout" in netlist
    assert "d_ref" in netlist
    assert ".param W =" in netlist or "W =" in netlist
    assert ".param L =" in netlist or "L =" in netlist


def test_current_mirror_generate_netlist_custom_params():
    """Current mirror generate_netlist() accepts custom width/length."""
    from app.circuits.current_mirror import generate_netlist

    netlist = generate_netlist(width=5.0, length=1.0)
    assert "5" in netlist
    assert "1" in netlist


def test_current_mirror_pipeline_run():
    """Run pipeline with current_mirror.py: DC/AC/transient netlists created and simulations produce results."""
    from app.models.circuit import ProcessStatus
    from app.services.pipeline_executor import PipelineExecutor
    from app.services.analysis_orchestrator import AnalysisOrchestrator

    circuit_path = ROOT / "app" / "circuits" / "current_mirror.py"
    if not circuit_path.exists():
        pytest.skip(f"Circuit file not found: {circuit_path}")

    process_id = "test_current_mirror_001"
    out_dir = ROOT / "data" / "designs"
    out_dir.mkdir(parents=True, exist_ok=True)

    # Clear if leftover from previous run
    if process_id in PipelineExecutor.processes:
        del PipelineExecutor.processes[process_id]

    PipelineExecutor.processes[process_id] = {
        "process_id": process_id,
        "status": ProcessStatus.RUNNING,
        "progress": 0,
        "results": None,
        "errors": [],
        "file_path": str(circuit_path),
        "filename": "current_mirror.py",
        "provided_parameters": {},
    }

    try:
        PipelineExecutor.run_circuit_from_file(
            process_id,
            str(circuit_path),
            {},
        )
    finally:
        if process_id in PipelineExecutor.processes:
            proc = PipelineExecutor.processes[process_id]
            status = proc["status"]
            results = proc.get("results") or {}
            errors = proc.get("errors", [])
            raw = results.get("raw_output", {})
            sim_errors = raw.get("errors", [])

    assert process_id in PipelineExecutor.processes
    proc = PipelineExecutor.processes[process_id]
    assert proc["status"] == ProcessStatus.COMPLETED, (
        f"Expected COMPLETED, got {proc['status']}; errors: {proc.get('errors')}; sim_errors: {sim_errors}"
    )
    assert proc.get("results") is not None
    netlists = proc["results"].get("netlists", {})
    assert "dc" in netlists and "ac" in netlists and "transient" in netlists
    assert Path(netlists["dc"]).exists() or (ROOT / netlists["dc"]).exists(), f"DC netlist missing: {netlists['dc']}"
    plots = proc["results"].get("plots", [])
    assert len(plots) == 3, f"Expected 3 plots (dc, ac, tran), got {len(plots)}: {plots}"
