# xEDA Frontend

React + Vite + TypeScript frontend for xEDA.

## Environment

Copy `.env.example` to `.env` and set:

```bash
VITE_API_BASE_URL=http://backend:8000
```

Use `http://backend:8000` in Docker networks, and an appropriate host URL in local non-Docker runs.

## Run with pnpm

```bash
pnpm install
pnpm dev
```

## Run with Docker

```bash
docker build -t xeda-frontend .
docker run -p 5173:5173 xeda-frontend
```
