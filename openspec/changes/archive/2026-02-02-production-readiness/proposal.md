# Proposal: Production Readiness & Docker Finalization

## Goal
Prepare the POST Clinics MVP (Backend + Dashboard + Agent) for production deployment using Docker.

## Current State Analysis
- **Backend**: FastAPI running on port 8000. SQLite persistence. Z-API webhook.
- **Frontend**: Vite (React/TS) running on dev server 5173. **Issue**: Dev server is not for production.
- **Agent**: Functional, with cleaned output.
- **Infrastructure**: Existing `Dockerfile` only covers Python. `docker-compose` only covers Backend.

## Plan
1. **Frontend Build**: configure Vite to build static assets (`dist/`).
2. **Serving**: Update FastAPI to serve these static files at root `/` (Single, simple container) OR add Nginx service. (Recommendation: Serve via FastAPI for simplest MVP deployment).
3. **Docker Update**: Modify `Dockerfile` to include Node.js (multi-stage build) or just build locally and copy `dist/`. *Decision: Multi-stage build (Node->Python) for self-contained reproduction.*
4. **Environment**: Ensure `.env` is properly passed.
5. **Verification**: Run `verify_full_system.py` against the *containerized* app.
