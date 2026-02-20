# POST Clinics System

Web application for appointment scheduling and management.

## 🚀 Production Deployment (VPS)

### Prerequisites
- Docker & Docker Compose installed on the VPS.
- Domain `clinics.posolutionstech.com.br` pointing to the VPS IP.

### Setup
1. **Clone the repository**:
   ```bash
   git clone <repo_url>
   cd noshowai_mvp
   ```

2. **Environment Configuration**:
   Create a `.env` file (see `.env.example`) with your production secrets:
   ```bash
   cp .env.example .env
   nano .env
   ```

3. **Start the Stack**:
   The production compose file sets up the App, Nginx, and Certbot (SSL).
   ```bash
   chmod +x init-letsencrypt.sh
   ./init-letsencrypt.sh
   # OR manually:
   docker-compose -f docker-compose.prod.yml up -d
   ```

### Architecture
- **Nginx**: Reverse Proxy (Ports 80/443) -> Handles SSL termination.
- **App**: FastAPI + React (Port 8000 internal).
- **Certbot**: Auto-renews Let's Encrypt certificates.
