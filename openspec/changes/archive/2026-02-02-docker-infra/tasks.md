# Implementation Tasks

## 1. Refactor for Persistence
- [x] 1.1 Update `src/config.py` to read `DATA_DIR` from environment (defaulting to `.`).
- [x] 1.2 Update `src/database.py` and `src/main.py` to construct database paths using `DATA_DIR`.

## 2. Containerization
- [x] 2.1 Create `.dockerignore` to exclude venv, git, temporary files, and local DBs.
- [x] 2.2 Create `Dockerfile` using `python:3.9-slim`. Install system deps if needed (sqlite3 is usually builtin, maybe build-essential for some pip packages?).

## 3. Orchestration
- [x] 3.1 Create `docker-compose.yml` defining the `app` service, mapping ports, env file, and volumes.

## 4. Documentation & Verification
- [x] 4.1 Update `README.md` with "How to Run with Docker" instructions.
- [x] 4.2 Verify `docker-compose up` works and data persists.
