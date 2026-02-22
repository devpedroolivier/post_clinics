from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import logging
import os

load_dotenv()

from src.infrastructure.database import create_db_and_tables
from src.api.routes import auth, appointments, webhooks

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PostClinics")

app = FastAPI(title="POST Clinics MVP")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(appointments.router)
app.include_router(webhooks.router)

@app.get("/api/health")
async def health_check():
    return {"message": "POST Clinics API is running"}

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    logger.info("Database tables verified.")

# Mount static files (Dashboard) - MUST BE LAST
static_dir = os.path.join(os.getcwd(), "static")
if not os.path.exists(static_dir):
    static_dir = os.path.join(os.getcwd(), "dashboard", "dist")

if os.path.exists(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
else:
    logger.warning(f"Static directory not found at {static_dir}. Dashboard will not be served.")

if __name__ == "__main__":
    import uvicorn
    # Using 0.0.0.0 is the standard for both VPS and Docker, same for local dev
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=True)
