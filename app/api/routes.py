"""API routes for the Zero Trust Network Access system."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/api")


class LoginRequest(BaseModel):
    username: str
    password: str


class MFARequest(BaseModel):
    username: str
    code: str


class EncryptRequest(BaseModel):
    plaintext: str


class SignRequest(BaseModel):
    message: str
    key_id: Optional[str] = None


class VerifyRequest(BaseModel):
    message: str
    signature_hex: str
    key_id: Optional[str] = None


class PolicyEvalRequest(BaseModel):
    resource: str
    role: str = "guest"
    trust_score: float = 50
    zone: str = "guest"
    has_mfa: bool = False
    has_pqc: bool = False


def create_routes(auth_handler, pqc_manager, trust_engine, policy_engine, store):
    """Create API routes with injected dependencies."""

    # --- Auth ---
    @router.post("/auth/login")
    async def login(req: LoginRequest):
        result = auth_handler.authenticate(req.username, req.password)
        if not result["success"]:
            raise HTTPException(status_code=401, detail=result["error"])
        store.stats["total_requests"] += 1
        return result

    @router.post("/auth/mfa")
    async def verify_mfa(req: MFARequest):
        result = auth_handler.verify_mfa(req.username, req.code)
        if not result["success"]:
            raise HTTPException(status_code=401, detail=result["error"])
        return result

    @router.get("/auth/sessions")
    async def get_sessions():
        return auth_handler.get_active_sessions()

    # --- Dashboard ---
    @router.get("/dashboard/stats")
    async def dashboard_stats():
        store.stats["active_sessions"] = len(auth_handler.get_active_sessions())
        stats = store.get_dashboard_stats()
        trust_data = trust_engine.compute_score()
        stats["trust_score"] = trust_data["trust_score"]
        stats["risk_level"] = trust_data["risk_level"]
        stats["trust_factors"] = trust_engine.get_all_factors()
        return stats

    @router.get("/dashboard/devices")
    async def dashboard_devices():
        return store.devices

    @router.get("/dashboard/threats")
    async def dashboard_threats():
        return store.get_recent_threats(50)

    @router.get("/dashboard/events")
    async def dashboard_events():
        return store.get_recent_events(50)

    # --- PQC ---
    @router.get("/pqc/status")
    async def pqc_status():
        return pqc_manager.get_full_status()

    @router.post("/pqc/keygen")
    async def pqc_keygen():
        result = pqc_manager.rotate_keys()
        store.stats["key_rotations"] += 1
        store.add_event({
            "type": "pqc_key_rotation",
            "detail": f"Keys rotated. KEM: {result['kem_key_id']}, DSA: {result['dsa_key_id']}",
            "severity": "info",
        })
        return result

    @router.post("/pqc/encrypt")
    async def pqc_encrypt(req: EncryptRequest):
        result = pqc_manager.encrypt_demo(req.plaintext)
        store.stats["pqc_encryptions"] += 1
        return result

    @router.post("/pqc/sign")
    async def pqc_sign(req: SignRequest):
        key_id = req.key_id or pqc_manager.active_dsa_key["key_id"]
        return pqc_manager.dilithium.sign(key_id, req.message)

    @router.post("/pqc/verify")
    async def pqc_verify(req: VerifyRequest):
        key_id = req.key_id or pqc_manager.active_dsa_key["key_id"]
        return pqc_manager.dilithium.verify(key_id, req.message, req.signature_hex)

    # --- Trust ---
    @router.get("/trust/score")
    async def trust_score():
        return trust_engine.compute_score()

    @router.get("/trust/factors")
    async def trust_factors():
        return trust_engine.get_all_factors()

    # --- Policies ---
    @router.get("/policies")
    async def list_policies():
        return policy_engine.get_policies()

    @router.post("/policies/evaluate")
    async def evaluate_policy(req: PolicyEvalRequest):
        store.stats["total_requests"] += 1
        result = policy_engine.evaluate(req.model_dump())
        if result["decision"] == "deny":
            store.stats["blocked_requests"] += 1
        return result

    @router.get("/policies/evaluations")
    async def recent_evaluations():
        return policy_engine.get_recent_evaluations()

    @router.get("/policies/zones")
    async def get_zones():
        return policy_engine.get_zones()

    # --- Network ---
    @router.get("/network/topology")
    async def network_topology():
        return store.topology

    @router.get("/network/segments")
    async def network_segments():
        return policy_engine.get_zones()

    return router
