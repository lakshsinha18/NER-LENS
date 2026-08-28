import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .api import router
from .config import get_settings
from .database import Base, SessionLocal, engine
from .services.demo_data import seed_demo_data
from .services.realtime import manager
from . import models  # noqa: F401 — registers SQLAlchemy models before create_all

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_demo_data(db)
    yield


app = FastAPI(title="NER-LENS API", version="0.1.0", description="Northeast India landslide early-warning prototype. Demo data is explicitly simulated.", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=[origin.strip() for origin in settings.cors_origins.split(",")], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(router)
app.mount("/uploads", StaticFiles(directory=str(settings.upload_path)), name="uploads")


@app.get("/health")
def health():
    return {"status": "ok", "mode": "DEMO / SIMULATED DATA", "service": "NER-LENS"}


@app.websocket("/ws/dashboard")
async def dashboard_socket(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keeps the connection open and permits client heartbeats.
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
