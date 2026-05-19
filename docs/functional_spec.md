# xEDA Functional Specification Document

## 1. Project Overview

### What xEDA Is
xEDA is an AI-assisted analog Electronic Design Automation (EDA) platform focused on analog circuit design and simulation workflows using the SkyWater SKY130 process design kit (PDK). It combines circuit template selection, parameterized netlist generation, simulation orchestration, data analysis, and visualization into one integrated environment.

### Why Analog EDA Automation Is Important
Analog IC design is still heavily iterative and expert-driven. Designers repeatedly tune transistor dimensions, biasing conditions, and topology choices while validating behavior over AC, DC, and transient analyses. Automation reduces repetitive work, improves reproducibility, and enables broader exploration of the design space.

### Problems With Traditional Analog Workflows
- High dependence on manual netlist editing and ad hoc scripts.
- Slow iteration loops between design changes and simulation feedback.
- Inconsistent documentation and poor experiment traceability.
- Difficulty reproducing prior runs due to environment differences.
- Limited accessibility for students and researchers without commercial toolchains.

### Why SKY130 Matters
SKY130 is a mature open-source PDK with a strong ecosystem. It allows transparent model access, reproducible research, and low-barrier prototyping for academia, startups, and independent engineers. Building on SKY130 aligns xEDA with open silicon initiatives.

### Main Objective of xEDA
Deliver a production-minded, extensible platform for AI-assisted analog design that can:
- Generate SKY130-aware SPICE netlists.
- Run and orchestrate NGSpice simulations.
- Analyze results against user specifications.
- Visualize and export design outcomes.
- Evolve toward autonomous analog synthesis workflows.

## 2. Vision Statement

xEDA aims to become an open, extensible foundation for analog design intelligence where human designers and AI systems collaborate across the full design loop.

### Long-Term Vision
- Build an engineering-grade platform for analog design automation from specification to simulation intelligence.
- Enable repeatable research and industrial prototyping in open silicon flows.

### AI-Assisted Analog Circuit Generation
- Translate performance goals into candidate topologies and parameter sets.
- Recommend simulation strategies and interpret failures with actionable guidance.

### Democratization of Analog Design
- Lower tooling barriers for education and small teams.
- Make advanced analog workflows accessible without proprietary EDA lock-in.

### Open-Source Accessibility
- Integrate with open PDK and simulation tooling.
- Encourage contribution through transparent architecture and modular design.

### Research and Educational Applications
- Support thesis/research workflows with reproducible simulations.
- Provide structured educational experiences for analog fundamentals.

## 3. Scope

### Included Functionality
- Circuit template catalog for analog building blocks.
- Parameter input and constraint validation.
- SKY130-aware SPICE netlist generation.
- AC, DC, and transient simulation orchestration via NGSpice.
- Result parsing and waveform/frequency visualization.
- Project persistence, result export, and netlist import.
- AI assistance for parameter suggestions and simulation guidance.

### Excluded Functionality (Current)
- Full physical layout generation and routing.
- Signoff DRC/LVS in the current runtime.
- Closed-loop autonomous tapeout pipeline.
- Proprietary PDK integration in MVP.

### Current MVP Scope
- Web-based workflow from circuit selection to simulation visualization.
- SKY130 netlist generation and NGSpice execution.
- User-guided AI recommendations for parameter exploration.

### Future Expansion Scope
- Monte Carlo and corner automation.
- Layout-aware analysis and DRC/LVS integration.
- Multi-PDK adaptation and cloud-scale simulation.
- Reinforcement-learning-driven design optimization.

## 4. User Roles

### Analog Design Engineer
- Permissions: create/edit projects, run simulations, export reports.
- Use Cases: circuit exploration, spec tuning, simulation comparison.
- Workflow: select topology -> enter constraints -> generate netlist -> simulate -> iterate.

### Researcher
- Permissions: all engineer capabilities plus experiment-heavy usage.
- Use Cases: benchmarking optimization methods, generating datasets.
- Workflow: define param studies -> run multiple simulations -> export structured data.

### Student
- Permissions: create projects, run guided flows, export assignment reports.
- Use Cases: learning analog behavior, validating textbook concepts.
- Workflow: choose template -> modify key parameters -> observe response shifts.

### Administrator
- Permissions: user/session management, environment configuration, operational controls.
- Use Cases: system health monitoring, model path setup, policy controls.
- Workflow: configure deployment -> maintain dependencies -> monitor jobs/logs.

### Future AI Agent Integration
- Permissions: policy-bound API-driven design and simulation actions.
- Use Cases: autonomous optimization loops and design assistants.
- Workflow: receive objective -> generate candidate designs -> simulate -> refine.

## 5. Functional Requirements

### 5.1 Circuit Design Module
- Provide circuit selection from supported analog templates.
- Collect parameterized inputs (W/L, bias currents, supply, load, temperature).
- Support device sizing updates and derived parameter calculations.
- Validate user constraints (gain, bandwidth, power, swing).
- Enforce technology-rule checks based on SKY130 constraints.

### 5.2 Netlist Generation Engine
- Generate SPICE netlists compatible with NGSpice.
- Map template devices to SKY130 model definitions.
- Support parameterized generation and repeatable substitution.
- Perform pre-simulation validation (syntax, connectivity, include/model checks).

### 5.3 Simulation Engine
- AC analysis: frequency sweep, gain/phase extraction, bandwidth estimation.
- DC analysis: operating point and param sweeps.
- Transient analysis: time-domain waveforms and dynamic response.
- Future support: Monte Carlo variability runs.
- Future support: corner analysis across process/voltage/temperature sets.

### 5.4 Visualization Module
- Plot waveforms for selected nodes and currents.
- Display gain-bandwidth and frequency response curves.
- Present operating point tables and derived metrics.
- Allow graph export in image and data formats.

### 5.5 AI Assistance Module
- Prompt-based circuit and setup suggestions.
- Intelligent parameter recommendations from target specs.
- Error interpretation for NGSpice/log messages.
- Simulation recommendation engine for next-best analysis runs.

### 5.6 File Management
- Save and load projects with metadata and artifacts.
- Version tracking of parameter/netlist revisions.
- Export reports including setup, plots, and conclusions.
- Import user netlists for simulation and analysis.

### 5.7 Authentication and User Management
- Login/logout with secure session handling.
- Role-based access control for protected actions.
- Session lifetime and revocation support.

## 6. Non-Functional Requirements

### Performance
- Fast UI response for parameter editing and visualization.
- Efficient simulation dispatch and result retrieval for typical analog block sizes.

### Scalability
- Handle concurrent simulation requests via worker-based execution.
- Support progressive migration to distributed compute.

### Reliability
- Deterministic netlist generation from identical inputs.
- Stable job-state tracking and restart-safe metadata persistence.

### Maintainability
- Clear module boundaries and typed interfaces.
- Testable components with documented APIs.

### Security
- Input validation for forms and uploaded netlists.
- Sandboxed simulation execution.
- Access controls and session protection.

### Portability
- Docker-based deployment across Linux environments.
- Environment consistency for dependencies and runtime tools.

### Extensibility
- Modular support for additional circuit templates and PDK adapters.
- Pluggable AI strategy integration.

### Usability
- Guided workflows for non-expert users.
- Clear, actionable validation and error feedback.

### Fault Tolerance
- Graceful handling of simulation failures and timeouts.
- Retry and recovery mechanisms for transient execution issues.

## 7. System Workflow

1. User selects a circuit template.
2. User inputs design parameters and target specifications.
3. Backend validates constraints and technology rules.
4. Netlist generator produces SKY130-aware SPICE netlist.
5. User configures simulation type and runtime settings.
6. Backend orchestrates NGSpice execution.
7. Parser extracts waveforms and metrics from outputs.
8. Frontend visualizes responses and computed indicators.
9. User compares runs, adjusts parameters, and iterates.
10. User exports report and artifacts.

### Workflow Notes
- Validation occurs both pre-netlist and pre-simulation.
- Artifacts are stored with metadata for reproducibility.
- AI recommendations can be injected before or after simulation runs.

## 8. User Stories

### US-01: Generate an OTA Netlist
As an analog design engineer, I want to generate a SKY130 OTA netlist from parameter inputs so that I can quickly begin simulation.
- Priority: High
- Acceptance Criteria:
  - Template and parameter form are available.
  - Valid input generates a syntactically correct netlist.
  - Netlist is saved and linked to a project.

### US-02: Run AC Simulation
As a researcher, I want to run AC analysis with configurable frequency ranges so that I can evaluate gain and phase margins.
- Priority: High
- Acceptance Criteria:
  - AC simulation settings are configurable.
  - Job status is trackable.
  - Frequency response and metrics are displayed.

### US-03: Export Waveforms
As a student, I want to export plotted waveforms so that I can include them in reports.
- Priority: Medium
- Acceptance Criteria:
  - Export format options are available.
  - Exported files match displayed data.

### US-04: Modify Device Parameters
As an analog design engineer, I want to adjust transistor W/L and rerun simulations so that I can optimize performance.
- Priority: High
- Acceptance Criteria:
  - Parameter edits are validated.
  - New netlist and simulation outputs reflect the changes.

### US-05: Compare Simulation Runs
As a researcher, I want to compare multiple simulation results side-by-side so that I can quantify design trade-offs.
- Priority: Medium
- Acceptance Criteria:
  - Multiple runs can be selected.
  - Overlay and metric deltas are shown.

## 9. Use Case Specifications

### UC-01: Generate OTA
- Actor: Analog Design Engineer
- Preconditions: Authenticated session, template available.
- Main Flow:
  1. Select OTA template.
  2. Enter parameters and constraints.
  3. Submit generation request.
  4. Review generated netlist.
- Postconditions: Netlist stored and ready for simulation.

### UC-02: Run AC Simulation
- Actor: Analog Design Engineer / Researcher
- Preconditions: Valid netlist available.
- Main Flow:
  1. Set AC sweep settings.
  2. Start simulation.
  3. Monitor execution status.
  4. View gain/phase outputs.
- Postconditions: Result artifacts and metrics are stored.

### UC-03: Export Waveform
- Actor: Student / Engineer
- Preconditions: Completed simulation with plotted data.
- Main Flow:
  1. Select waveform and format.
  2. Trigger export.
  3. Download artifact.
- Postconditions: Exported file available for documentation.

### UC-04: Modify Transistor Parameters
- Actor: Analog Design Engineer
- Preconditions: Existing project with editable parameters.
- Main Flow:
  1. Update W/L or bias values.
  2. Revalidate constraints.
  3. Regenerate netlist and rerun simulation.
- Postconditions: Updated simulation result is available.

### UC-05: Compare Simulations
- Actor: Researcher
- Preconditions: Two or more completed runs.
- Main Flow:
  1. Select runs to compare.
  2. Generate overlays and computed deltas.
  3. Save comparison report.
- Postconditions: Comparative insights are persisted.

## 10. Constraints and Assumptions

### Constraints
- Dependence on SKY130 model file integrity and compatibility.
- Numerical convergence limits inherent to SPICE simulation.
- Runtime limits on local compute for large sweeps.

### Assumptions
- Users understand baseline analog/SPICE concepts.
- NGSpice and PySpice environments are configured correctly.
- Dockerized deployment provides stable dependency control.

## 11. Risk Analysis

### PDK Compatibility Risks
- Model updates or path mismatches may break netlist execution.
- Mitigation: version pinning, startup checks, compatibility tests.

### Simulation Instability
- Convergence failures may interrupt iterative workflows.
- Mitigation: robust option presets, automatic diagnostics, retry strategies.

### Incorrect Netlist Generation
- Parameter substitution errors can create invalid decks.
- Mitigation: schema validation, linting, regression test vectors.

### UI/Backend Synchronization Risks
- Inconsistent schema versions may cause runtime errors.
- Mitigation: shared typed contracts and versioned APIs.

## 12. Future Features

- AI agent workflows for autonomous exploration loops.
- Reinforcement-learning optimization for transistor sizing.
- Layout generation and parasitic-aware analysis.
- LVS/DRC integration in open-source physical verification flow.
- Autonomous analog synthesis with objective-driven iteration.
- Multi-PDK support beyond SKY130.

## 13. Conclusion

xEDA addresses a critical gap in analog design productivity by unifying SKY130-aware netlist generation, simulation orchestration, analysis, and AI guidance into a single platform. Its functional scope supports immediate MVP utility while establishing a robust foundation for future autonomous and layout-aware analog design workflows.
