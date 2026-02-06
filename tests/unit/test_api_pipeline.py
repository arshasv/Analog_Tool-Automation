"""
Unit tests for API pipeline
Tests the circuit API endpoints and PipelineExecutor
"""
import sys
import os
import asyncio
import json
import tempfile
from pathlib import Path
from io import BytesIO

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.circuit import ProcessStatus
from app.services.pipeline_executor import PipelineExecutor


@pytest.fixture(autouse=True)
def cleanup_processes():
    """Clean up processes before and after each test"""
    PipelineExecutor.processes.clear()
    yield
    PipelineExecutor.processes.clear()


@pytest.fixture
def client():
    """FastAPI test client"""
    return TestClient(app)


class TestAPIEndpoints:
    """Test FastAPI circuit API endpoints"""
    
    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
    
    def test_root_endpoint(self, client):
        """Test root endpoint returns available endpoints"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "api" in data
        assert "endpoints" in data
        assert len(data["endpoints"]) > 0
    
    def test_run_without_file(self, client):
        """Test /run endpoint fails without file"""
        response = client.post("/api/v1/run")
        assert response.status_code == 422  # Unprocessable entity (missing file)
    
    def test_run_with_simple_circuit_file(self, client):
        """Test /run endpoint with a simple circuit file"""
        # Create a minimal circuit file
        circuit_code = '''
"""Test circuit"""
PARAMETERS = {
    "iref": 1e-5,
    "vdd": 1.8,
}

def build_circuit(**kwargs):
    return {"netlist": "minimal circuit"}
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(circuit_code)
            f.flush()
            temp_path = f.name
        
        try:
            # Upload file
            with open(temp_path, 'rb') as f:
                files = {'file': ('test_circuit.py', f, 'text/plain')}
                response = client.post("/api/v1/run", files=files)
            
            assert response.status_code == 200
            data = response.json()
            assert "process_id" in data
            assert data["status"] == ProcessStatus.RUNNING
            # Filename is prefixed with process_id by the API
            assert data["filename"].endswith("test_circuit.py")
            assert data["parameters"]["iref"] == 1e-5
            assert data["parameters"]["vdd"] == 1.8
            
        finally:
            os.unlink(temp_path)
    
    def test_run_with_parameters_override(self, client):
        """Test /run endpoint with custom parameters"""
        circuit_code = '''
PARAMETERS = {
    "iref": 1e-5,
    "length": 0.5,
}
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(circuit_code)
            f.flush()
            temp_path = f.name
        
        try:
            # Upload file with parameter override
            with open(temp_path, 'rb') as f:
                files = {'file': ('circuit.py', f, 'text/plain')}
                params = '{"iref": 2e-5, "length": 1.0}'
                response = client.post(
                    "/api/v1/run",
                    files=files,
                    data={"parameters": params}
                )
            
            assert response.status_code == 200
            data = response.json()
            # Override should apply
            assert data["parameters"]["iref"] == 2e-5
            assert data["parameters"]["length"] == 1.0
            
        finally:
            os.unlink(temp_path)
    
    def test_status_nonexistent_process(self, client):
        """Test status endpoint with nonexistent process"""
        response = client.get("/api/v1/status/nonexistent_process")
        assert response.status_code == 404


class TestPipelineExecutor:
    """Test PipelineExecutor functionality"""
    
    def test_parse_parameters_from_dict(self):
        """Test parsing PARAMETERS dict from circuit file"""
        circuit_code = '''
PARAMETERS = {
    "iref": 1e-5,
    "vdd": 1.8,
    "length": 0.5,
}

def build_circuit(**kwargs):
    pass
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(circuit_code)
            f.flush()
            temp_path = f.name
        
        try:
            params = PipelineExecutor.parse_parameters_from_file(temp_path)
            
            assert len(params) == 3
            param_names = {p["name"] for p in params}
            assert param_names == {"iref", "vdd", "length"}
            
            # Check defaults
            iref_param = next(p for p in params if p["name"] == "iref")
            assert iref_param["default"] == 1e-5
            
        finally:
            os.unlink(temp_path)
    
    def test_parse_parameters_from_function_signature(self):
        """Test parsing parameters from build_circuit function signature"""
        circuit_code = '''
def build_circuit(iref=1e-5, vdd=1.8, length=0.5):
    """Build circuit with defaults"""
    pass
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(circuit_code)
            f.flush()
            temp_path = f.name
        
        try:
            params = PipelineExecutor.parse_parameters_from_file(temp_path)
            
            assert len(params) == 3
            param_names = {p["name"] for p in params}
            assert param_names == {"iref", "vdd", "length"}
            
        finally:
            os.unlink(temp_path)
    
    def test_parse_parameters_empty_file(self):
        """Test parsing parameters from file with no PARAMETERS or build_circuit"""
        circuit_code = '''
# Just some random python code
x = 5
y = 10
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(circuit_code)
            f.flush()
            temp_path = f.name
        
        try:
            params = PipelineExecutor.parse_parameters_from_file(temp_path)
            assert params == []
            
        finally:
            os.unlink(temp_path)
    
    @pytest.mark.asyncio
    async def test_run_circuit_from_file(self):
        """Test running circuit from uploaded file"""
        circuit_code = '''
PARAMETERS = {
    "iref": 1e-5,
}
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, dir='data/designs/uploads') as f:
            f.write(circuit_code)
            f.flush()
            temp_path = f.name
        
        try:
            os.makedirs('data/designs', exist_ok=True)
            
            process_id = "test_proc_123"
            PipelineExecutor.processes[process_id] = {
                "process_id": process_id,
                "status": ProcessStatus.PENDING,
                "progress": 0,
            }
            
            await PipelineExecutor.run_circuit_from_file(
                process_id, 
                temp_path,
                {"iref": 1.5e-5}
            )
            
            proc = PipelineExecutor.processes[process_id]
            assert proc["status"] == ProcessStatus.COMPLETED
            assert proc["progress"] == 100
            assert proc["results"] is not None
            assert "netlist_path" in proc["results"]
            assert "simulation_output" in proc["results"]
            
        finally:
            # Cleanup
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            if process_id in PipelineExecutor.processes:
                PipelineExecutor.processes.pop(process_id, None)


class TestEndToEnd:
    """End-to-end integration tests"""
    
    def test_full_pipeline_flow(self, client):
        """Test complete flow: upload -> check status -> get results"""
        circuit_code = '''
PARAMETERS = {
    "width": 2.0,
    "length": 0.5,
}
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(circuit_code)
            f.flush()
            temp_path = f.name
        
        try:
            # Step 1: Upload circuit
            with open(temp_path, 'rb') as f:
                files = {'file': ('circuit.py', f, 'text/plain')}
                response = client.post("/api/v1/run", files=files)
            
            assert response.status_code == 200
            run_data = response.json()
            process_id = run_data["process_id"]
            assert run_data["status"] == ProcessStatus.RUNNING
            
            # Step 2: Poll status
            import time
            time.sleep(2)  # Give it time to process
            
            status_response = client.get(f"/api/v1/status/{process_id}")
            assert status_response.status_code == 200
            status_data = status_response.json()
            
            # Should be completed or nearly there
            assert status_data["process_id"] == process_id
            assert status_data["status"] in [ProcessStatus.RUNNING, ProcessStatus.COMPLETED]
            
        finally:
            os.unlink(temp_path)


def run_all_tests():
    """Run all tests"""
    pytest.main([__file__, "-v", "-s"])


if __name__ == "__main__":
    run_all_tests()
