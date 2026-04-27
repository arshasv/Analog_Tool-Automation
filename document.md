# xEDA Project Documentation for React UI Integration

## Project Overview

xEDA is an EDA (Electronic Design Automation) tool for analog/mixed-signal circuit design and optimization. It features a modular Python backend for circuit analysis, synthesis, and simulation, leveraging SPICE and the Sky130 PDK.

---

## Project Structure

- **app/**: Main backend application (Python, FastAPI/Flask style).
  - **api/**: API endpoints for circuits and related operations.
  - **circuits/**: Circuit models and building blocks.
  - **core/**: Core logic, configuration, and optimization routines.
  - **models/**: Data models (likely Pydantic or similar).
  - **services/**: Service layer for orchestration, simulation, and synthesis.
  - **utils/**: Utility functions (e.g., plotting).
- **pdk/**: Process Design Kit files (Sky130, SPICE libraries).
- **tests/**: Test cases and SPICE testbenches.
- **Dockerfile / docker-compose.yml**: Containerization for deployment.
- **requirements.txt**: Python dependencies.

---

## Backend API (for React Integration)

### 1. API Endpoints

- The backend likely exposes RESTful endpoints under `app/api/`.
- Endpoints may include:
  - Circuit creation, listing, and details
  - Simulation requests (DC, AC, transient)
  - Parameter optimization
  - Result retrieval (plots, data)
- Check `app/api/circuits.py` and related files for endpoint definitions.

### 2. Data Models

- Data exchanged via JSON (circuit parameters, simulation configs, results).
- Models defined in `app/models/`.

### 3. Running the Backend

- Use Docker or a Python virtual environment.
- Start the backend server (e.g., `uvicorn app.main:app` or similar).
- Ensure the backend is accessible (e.g., http://localhost:8000).

---

## Recommendations for React UI

### 1. UI Features

- Circuit selection and configuration
- Parameter input forms
- Simulation controls (run, stop, view logs)
- Visualization of results (plots, tables)
- Optimization workflow (set goals, view progress)
- File upload/download (SPICE netlists, results)

### 2. API Integration

- Use Axios or Fetch for HTTP requests.
- Define a service layer in React for API calls.
- Handle authentication if required (token-based).

### 3. State Management

- Use React Context or Redux for global state (circuits, results, user session).

### 4. Visualization

- Use charting libraries (e.g., Chart.js, Recharts, Plotly) for simulation results.
- Consider schematic/circuit diagram rendering (SVG, custom components).

### 5. Deployment

- Serve the React app separately (default: http://localhost:3000) or via the backend (using a static files route).
- Use Docker Compose for full-stack deployment.

---

## Getting Started

1. **Backend**:  
   - Set up Python environment (`requirements.txt`).
   - Run backend server.

2. **Frontend**:  
   - Scaffold React app (`npx create-react-app xeda-ui`).
   - Set up API service layer.
   - Build UI components for workflows above.

3. **Connect**:  
   - Configure API base URL in React.
   - Test end-to-end flows (circuit creation → simulation → results).

---

## Useful References

- [ARCHITECTURE_SEARCH_GUIDE.md](ARCHITECTURE_SEARCH_GUIDE.md): Backend architecture details.
- [README.md](README.md): Project overview and setup.
- [optimizer_params.md](optimizer_params.md): Optimization parameters.
- [Dockerfile](Dockerfile), [docker-compose.yml](docker-compose.yml): Deployment.

---

## Notes

- Review backend API endpoints and data models before UI development.
- Consider adding OpenAPI/Swagger docs to the backend for easier frontend integration.
- Use environment variables for API URLs in React.

---

This documentation should help you plan and implement a React UI for xEDA. If you need a more detailed API spec or UI wireframes, let me know!
