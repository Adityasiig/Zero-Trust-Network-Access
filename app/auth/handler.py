"""Authentication handler with JWT and device verification."""
import time
import hashlib
import os
from jose import jwt
from app.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES


DEMO_USERS = {
    "admin": {
        "username": "admin",
        "password_hash": hashlib.sha256(b"admin123").hexdigest(),
        "role": "admin",
        "mfa_enabled": True,
    },
    "engineer": {
        "username": "engineer",
        "password_hash": hashlib.sha256(b"eng123").hexdigest(),
        "role": "engineer",
        "mfa_enabled": True,
    },
    "analyst": {
        "username": "analyst",
        "password_hash": hashlib.sha256(b"analyst123").hexdigest(),
        "role": "analyst",
        "mfa_enabled": False,
    },
    "guest": {
        "username": "guest",
        "password_hash": hashlib.sha256(b"guest123").hexdigest(),
        "role": "guest",
        "mfa_enabled": False,
    },
}


class AuthHandler:
    """Handles authentication, JWT tokens, and device verification."""

    def __init__(self):
        self.active_sessions = {}
        self.mfa_codes = {}

    def authenticate(self, username: str, password: str) -> dict:
        user = DEMO_USERS.get(username)
        if not user:
            return {"success": False, "error": "User not found"}

        pw_hash = hashlib.sha256(password.encode()).hexdigest()
        if pw_hash != user["password_hash"]:
            return {"success": False, "error": "Invalid credentials"}

        if user["mfa_enabled"]:
            code = str(int.from_bytes(os.urandom(3), "big") % 1000000).zfill(6)
            self.mfa_codes[username] = {
                "code": code,
                "expires": time.time() + 300,
            }
            return {
                "success": True,
                "requires_mfa": True,
                "mfa_code_hint": code,
                "username": username,
            }

        return self._create_session(username, user)

    def verify_mfa(self, username: str, code: str) -> dict:
        stored = self.mfa_codes.get(username)
        if not stored:
            return {"success": False, "error": "No MFA challenge pending"}
        if time.time() > stored["expires"]:
            del self.mfa_codes[username]
            return {"success": False, "error": "MFA code expired"}
        if stored["code"] != code:
            return {"success": False, "error": "Invalid MFA code"}

        del self.mfa_codes[username]
        user = DEMO_USERS[username]
        return self._create_session(username, user)

    def _create_session(self, username: str, user: dict) -> dict:
        session_id = hashlib.sha256(
            f"{username}{time.time()}{os.urandom(16).hex()}".encode()
        ).hexdigest()[:24]

        payload = {
            "sub": username,
            "role": user["role"],
            "session_id": session_id,
            "mfa": user["mfa_enabled"],
            "exp": time.time() + ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

        self.active_sessions[session_id] = {
            "username": username,
            "role": user["role"],
            "token": token,
            "created": time.time(),
            "mfa_verified": user["mfa_enabled"],
        }

        return {
            "success": True,
            "token": token,
            "session_id": session_id,
            "role": user["role"],
            "mfa_verified": user["mfa_enabled"],
        }

    def verify_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return {"valid": True, "payload": payload}
        except Exception as e:
            return {"valid": False, "error": str(e)}

    def get_active_sessions(self) -> list:
        now = time.time()
        active = []
        for sid, session in self.active_sessions.items():
            age = now - session["created"]
            if age < ACCESS_TOKEN_EXPIRE_MINUTES * 60:
                active.append({
                    "session_id": sid,
                    "username": session["username"],
                    "role": session["role"],
                    "age_seconds": round(age),
                    "mfa_verified": session["mfa_verified"],
                })
        return active
