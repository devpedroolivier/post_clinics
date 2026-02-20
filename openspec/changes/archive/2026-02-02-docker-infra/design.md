# Design: Docker Infrastructure

## Context
The application is currently a FastAPI MVP running directly on the host machine. Dependencies are managed via `requirements.txt`. Data is stored in local SQLite files.

## Goals / Non-Goals
**Goals:**
- Create a production-ready Docker image.
- Automate persistent storage setup via Docker Compose.
- Update application configuration to support dynamic data paths.

**Non-Goals:**
- Kubernetes deployment specs (out of scope for MVP).
- CI/CD pipeline integration (future step).

## Decisions
- **Base Image**: Use `python:3.9-slim` for a balance of size and compatibility.
- **Volume Strategy**: Use a named volume or bind mount mapped to `/app/data` inside the container. The application will be refactored to check a `DATA_DIR` environment variable.
- **Environment Variables**: Use `.env` file passed to Docker Compose.
- **User**: Run as a non-root user (good practice) if possible, but for MVP/Windows host simplicity, root inside container is acceptable initially if permission issues arise.

## Risks / Trade-offs
- **Persistence**: If the volume mapping is incorrect, data will be lost on container recreation. Mitigation: Explicit validation in specs.
- **Windows compatibility**: Docker on Windows can have filesystem quirks. We will use standard bind mounts or named volumes which are generally stable.
