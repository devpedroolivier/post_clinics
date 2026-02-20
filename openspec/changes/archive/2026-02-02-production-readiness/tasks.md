# Tasks: Production Readiness

## 1. Frontend Integration
- [ ] 1.1 Run `npm run build` in `dashboard/` to generate `dist/`.
- [ ] 1.2 Update `src/main.py` to mount `dashboard/dist` as StaticFiles at `/`.
- [ ] 1.3 Ensure SPA routing (redirect 404s to index.html) if needed.

## 2. Docker Updates
- [ ] 2.1 Update `Dockerfile` to use Multi-Stage Build:
    - Stage 1: Node.js (Build Frontend)
    - Stage 2: Python (Install Req + Copy Frontend Dist)
- [ ] 2.2 Update `docker-compose.yml` to rely on the new build.

## 3. Verification
- [ ] 3.1 Stop local uvicorn/vite.
- [ ] 3.2 Run `docker-compose up --build`.
- [ ] 3.3 Verify accessing `http://localhost:8000` loads the Dashboard.
- [ ] 3.4 Verify Agent Webhook is reachable.
