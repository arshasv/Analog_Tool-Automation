# xEDA Automation - scaffold

This repository provides a scaffolded Dockerized FastAPI service to automate EDA simulations using ngspice and PySpice.

<<<<<<< HEAD
=======
Quick notes:
- create pdk & work then,
- Place your Sky130 PDK (or symlink) under `./pdk` on the host before starting the container.
- Work directory for uploads and outputs is `./work` (mounted into container as `/work`).

>>>>>>> 796414ad0fcf47b20b8b3b923df1f251ece64da0
Endpoints (Swagger available at `/docs`):
- `POST /simulate` - upload a `.sp` (SPICE) or other file. Returns a `job_id`.
- `GET /status/{job_id}` - check job status.
- `GET /result/{job_id}` - download zip containing `.sp`, `.png` and logs.

Run locally with Docker Compose:

```bash
docker compose up --build
```

Security notes:
- The current scaffold may execute uploaded netlists with ngspice and create files; do not expose this service publicly without proper sandboxing and authentication.
