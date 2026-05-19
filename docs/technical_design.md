# xEDA Technical Design Document

## 1. System Architecture Overview

xEDA uses a modular, service-oriented architecture to support analog design workflows from specification entry to simulation visualization.

### Core Architectural Principles
- Strong separation between UI, orchestration, and simulation execution.
- Deterministic netlist generation using parameterized templates.
- Isolated simulation execution for security and reproducibility.
- Structured artifact management for traceability and scaling.

### Frontend/Backend Separation
- Frontend (React + TypeScript): user interaction, visualization, and workflow control.
- Backend (Python services): netlist generation, validation, simulation orchestration, parsing, and AI-assisted recommendation.

### Simulation Orchestration
- The backend submits simulation jobs to controlled execution workers.
- NGSpice is invoked in batch mode with generated netlists.
- Logs and output artifacts are collected and parsed into structured outputs.

### Data Flow Summary
User -> Frontend -> API -> Netlist Generation -> Simulation Worker -> NGSpice -> Parser -> Metrics Store -> Frontend Visualization

## 2. Technology Stack

### Python Backend
- Chosen for rapid scientific tooling integration and mature ecosystem.
- Supports orchestration logic, API services, and parser implementation.

### SciPy
- Used for numerical post-processing, signal analysis, and optimization support.
- Enables metric extraction from raw simulation data.

### NGSpice
- Core analog simulation engine for AC, DC, and transient analysis.
- Open-source compatibility with SKY130 model flows.

### PySpice
- Programmatic bridge from Python to SPICE workflows.
- Simplifies simulation pipeline integration and output handling.

### React Frontend
- Component-based UI suitable for complex design and visualization workflows.
- Supports interactive dashboards and iterative design loops.

### TypeScript
- Improves reliability through static typing and contract-safe API integration.
- Reduces runtime frontend errors and improves maintainability.

### Vite
- Fast development cycle and optimized build pipeline.
- Good fit for modern React + TypeScript projects.

### Docker Infrastructure
- Ensures reproducible build/runtime environments.
- Encapsulates simulation dependencies and OS-level tools.

### SKY130 Integration
- Open PDK alignment for model-level realism and reproducibility.
- Allows transparent model includes and parameter constraints.

## 3. High-Level Architecture

### Frontend Layer
- Design workspace, parameter forms, simulation controls, result dashboards.

### API Layer
- REST endpoints for generation, simulation, export, and AI assistance.
- Input validation and authentication enforcement.

### Simulation Layer
- Job dispatcher and worker execution runtime for NGSpice tasks.

### Netlist Generation Layer
- Template engine with SKY130-aware model mapping and parameter substitution.

### Data Processing Layer
- Parses simulation outputs into standardized datasets and computed metrics.

### Visualization Layer
- Interactive plotting of waveforms, Bode plots, sweeps, and operating points.

### Module Interactions
- Frontend submits typed payloads to API.
- API validates and invokes netlist/simulation services.
- Simulation results are parsed and returned in visualization-ready format.

## 4. Backend Design

### 4.1 Simulation Controller
Responsibilities:
- Accept simulation requests.
- Queue and dispatch jobs.
- Track lifecycle states: queued, running, completed, failed.

Internal Workflow:
1. Validate request payload and references.
2. Resolve netlist and simulation config.
3. Dispatch to worker runtime.
4. Collect status, logs, and outputs.
5. Trigger parser and persist metrics.

### 4.2 Netlist Parser/Generator
Responsibilities:
- Generate SPICE decks from parameterized templates.
- Validate generated decks and imported netlists.

Data Structures:
- Template specification (parameters, defaults, constraints).
- Netlist metadata (template id, param snapshot, version, timestamp).

### 4.3 Parameter Engine
Responsibilities:
- Enforce numeric ranges and technology constraints.
- Evaluate derived values and consistency checks.

### 4.4 AI Orchestration Layer
Responsibilities:
- Process prompt-driven requests.
- Generate suggestions for topology parameters and simulation strategies.
- Convert simulator/log errors into engineering guidance.

### 4.5 File Management System
Responsibilities:
- Organize project data, netlists, logs, and result artifacts.
- Version project revisions and simulation runs.

### 4.6 Logging Subsystem
Responsibilities:
- Capture service logs, simulation logs, and parser diagnostics.
- Provide searchable diagnostics for troubleshooting.

### 4.7 Error Handling System
Responsibilities:
- Standardize exception mapping and API-safe error responses.
- Surface human-readable remediation guidance.

## 5. Frontend Design

### React Component Hierarchy
- App shell and routing.
- Project/workspace pages.
- Parameter editors and simulation controls.
- Result visualizers and export modules.
- AI assistant interaction panel.

### State Management
- Typed application state for project context, forms, jobs, and results.
- Clear separation of transient UI state and persisted backend data.

### User Interaction Flow
1. Select or create project.
2. Choose circuit and set parameters.
3. Generate netlist and configure simulations.
4. Run simulation and monitor job status.
5. Analyze visual results and export outputs.

### Simulation Dashboard
- Job queue overview.
- Status indicators.
- Live logs and completed-run summaries.

### Visualization Rendering
- Efficient line rendering for waveform datasets.
- Overlay/compare support for multiple runs.
- Cursor and metric inspection tools.

### Form Validation
- Client-side validation aligned with backend schema contracts.
- Immediate feedback for constraint violations.

### Suggested Frontend Structure
- src/components
- src/pages
- src/services
- src/hooks
- src/store
- src/types
- src/utils

## 6. NGSpice Integration

### SPICE Invocation
- NGSpice executed in non-interactive batch mode from backend workers.
- Input netlists and model includes are mounted into controlled runtime.

### Dynamic Netlist Generation
- Simulation directives (AC/DC/TRAN) injected based on request config.
- Parameter substitutions ensure run-specific netlist materialization.

### Simulation Execution Pipeline
1. Validate netlist and model paths.
2. Create execution workspace.
3. Run NGSpice with runtime limits.
4. Capture stdout/stderr and output files.
5. Parse and store results.

### Output Parsing
- Extract vectors, sweeps, node values, and derived metrics.
- Normalize data format for frontend consumption.

### Error Handling
- Parse simulator logs for syntax/model/convergence errors.
- Return classified error objects with guidance.

### Parameter Sweeps and Batch Runs
- Support controlled sweep matrices.
- Aggregate run metadata and result summaries.

## 7. SKY130 Integration

### PDK Structure Integration
- Backend references SKY130 model libraries from configured paths.
- Model include directives are inserted by the generator.

### Device Libraries and Model Inclusion
- Supported primitive and macro mappings are maintained in a device map.
- Netlists include proper model sections for selected analyses.

### Design Rule Considerations
- Parameter checks enforce minimum geometries and safe ranges.
- Tooling prevents invalid combinations before simulation dispatch.

### Parameter Constraints
- W/L, multiplicity, and bias ranges validated against SKY130 assumptions.

### DRC-Safe Dimension Handling
- Current scope: pre-layout dimensional sanity checks.
- Future scope: full DRC/LVS integration.

## 8. API Design

### REST API Structure
- POST /generate-netlist
- POST /run-simulation
- POST /export-results
- POST /upload-netlist
- POST /ai-assist

### Endpoint Definitions

#### POST /generate-netlist
Request:
- project_id
- circuit_type
- parameters
- constraints

Response:
- netlist_id
- netlist_preview
- validation_messages

#### POST /run-simulation
Request:
- project_id
- netlist_id
- simulation_type
- simulation_config

Response:
- job_id
- status
- queued_at

#### POST /export-results
Request:
- project_id
- run_ids
- export_format

Response:
- export_id
- download_path

#### POST /upload-netlist
Request:
- project_id
- netlist_file

Response:
- netlist_id
- parse_status
- warnings

#### POST /ai-assist
Request:
- project_id
- prompt
- context

Response:
- suggestions
- rationale
- recommended_next_actions

### Error Response Contract
- code
- message
- details
- trace_id

### Authentication Flow
- Token-based session model.
- Role checks on protected endpoints.
- Session expiration and renewal controls.

## 9. Database / Storage Design

### Project Storage
- Project metadata and run index persisted in lightweight database.

### Simulation Result Storage
- Raw outputs and parsed datasets stored in structured artifact directories.

### File Organization
- project/{project_id}/netlists/
- project/{project_id}/runs/{run_id}/
- project/{project_id}/exports/

### Metadata Handling
- Track parameter snapshots, tool versions, timestamps, and status.

### Future Scalability
- Migrate to external database and object storage for distributed deployment.

## 10. Data Flow

1. User submits design input from frontend.
2. Backend validates and generates netlist.
3. Simulation request creates a queued job.
4. Worker executes NGSpice and collects outputs.
5. Parser derives structured metrics and waveform datasets.
6. Frontend retrieves and renders results.
7. User exports artifacts and report packages.

## 11. Error Handling Strategy

### Simulation Crashes
- Detect non-zero exits.
- Preserve logs and return classified faults.

### Invalid Netlists
- Preflight parsing before dispatch.
- Reject with line-level diagnostics where available.

### Missing Model Files
- Startup and per-run model path verification.
- Fail fast with corrective action hints.

### Numerical Convergence Issues
- Apply recommended solver options and retry policy.
- Present engineering suggestions to user.

### Frontend/Backend Communication Failures
- Retry-safe request patterns and clear status polling behavior.

## 12. Security Considerations

- Validate and sanitize file uploads.
- Restrict simulation runtime environment (sandboxing and resource limits).
- Enforce authentication and role-based authorization.
- Prevent command injection through strict invocation patterns.
- Protect session tokens and sensitive configuration.

## 13. Performance Optimization

- Simulation result caching for identical netlist/config signatures.
- Parallel worker execution for independent jobs.
- Asynchronous job processing and non-blocking API behavior.
- Result compression for transfer efficiency.
- Optimized frontend rendering for large waveform datasets.

## 14. Scalability Strategy

- Horizontal worker scaling for increased simulation throughput.
- Container orchestration readiness for clustered deployment.
- Future distributed queue and remote artifact storage.
- Progressive decomposition into microservices when scale demands.

## 15. DevOps and Deployment

### Docker Usage
- Containerized backend, frontend, and simulation runtime.
- Controlled dependency versions across environments.

### Docker Compose Architecture
- Service definitions for web UI, API, simulation workers, and storage.

### Environment Management
- Config-driven runtime with environment-variable overlays.

### CI/CD Possibilities
- Automated linting, tests, and container build pipelines.
- Tagged releases and reproducible deployment artifacts.

### Version Control Strategy
- Branch-based workflow with review gates and regression checks.

## 16. Folder Structure

Suggested enterprise-aligned structure:

- app/
  - api/
  - circuits/
  - services/
  - models/
  - utils/
  - core/
- frontend/
  - src/components/
  - src/pages/
  - src/services/
  - src/store/
- pdk/
  - sky130A/
- data/
  - designs/
  - results/
- tests/
- docs/
- infra/

## 17. Testing Strategy

### Unit Testing
- Netlist generator logic and parameter validation rules.
- Parser behavior for known NGSpice outputs.

### Integration Testing
- End-to-end simulation execution from generated netlist to parsed results.

### Simulation Validation
- Golden-reference comparison for key analog metrics.

### Frontend Testing
- Component tests for forms/visualizers.
- Workflow tests for job creation and result rendering.

### Regression Testing
- Baseline suite for supported circuit templates and APIs.

## 18. Future Technical Enhancements

- AI-based sizing optimization loops.
- RL-driven analog synthesis policies.
- Layout-aware simulation integration.
- Cloud-scale simulation farm support.
- Multi-user collaborative design sessions.

## 19. Conclusion

xEDA is designed as a technically grounded, modular analog EDA platform with a clear path from MVP utility to advanced autonomous workflows. The architecture aligns open SKY130 design goals with reproducible simulation infrastructure, robust API boundaries, and extensible AI-assisted engineering capabilities.
