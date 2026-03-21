"""
Zero Trust Network Access with Post-Quantum Cryptography
FastAPI Application Assembly
"""
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from app.pqc.manager import PQCManager
from app.trust.engine import TrustEngine
from app.policies.engine import PolicyEngine
from app.auth.handler import AuthHandler
from app.storage.store import DataStore
from app.api.routes import create_routes
from app.api.websocket import websocket_endpoint, ws_manager
from app.simulation.simulator import NetworkSimulator

# Initialize components
store = DataStore()
pqc_manager = PQCManager()
trust_engine = TrustEngine()
policy_engine = PolicyEngine()
auth_handler = AuthHandler()
simulator = NetworkSimulator(store, trust_engine, pqc_manager, ws_manager)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start simulation on startup, stop on shutdown."""
    sim_task = asyncio.create_task(simulator.start())
    yield
    await simulator.stop()
    sim_task.cancel()


app = FastAPI(
    title="Zero Trust Network Access - Post-Quantum Cryptography",
    description="ZTNA system with CRYSTALS-Kyber and CRYSTALS-Dilithium PQC algorithms",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
api_router = create_routes(auth_handler, pqc_manager, trust_engine, policy_engine, store)
app.include_router(api_router)

# WebSocket
app.websocket("/ws/live-feed")(websocket_endpoint)

# Serve dashboard
app.mount("/dashboard", StaticFiles(directory="dashboard", html=True), name="dashboard")


@app.get("/")
async def root():
    return FileResponse("dashboard/index.html")


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "ZTNA-PQC",
        "version": "1.0.0",
        "pqc_active": True,
        "quantum_safe": True,
    }
