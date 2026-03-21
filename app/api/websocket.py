"""WebSocket handler for real-time dashboard updates."""
import asyncio
import json
import time
from fastapi import WebSocket, WebSocketDisconnect


class ConnectionManager:
    """Manages WebSocket connections for live dashboard updates."""

    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        message["timestamp"] = time.time()
        data = json.dumps(message, default=str)
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(data)
            except Exception:
                disconnected.append(connection)
        for conn in disconnected:
            self.disconnect(conn)

    @property
    def connection_count(self) -> int:
        return len(self.active_connections)


ws_manager = ConnectionManager()


async def websocket_endpoint(websocket: WebSocket):
    """Handle WebSocket connections for real-time updates."""
    await ws_manager.connect(websocket)
    try:
        await websocket.send_text(json.dumps({
            "type": "connection_established",
            "message": "Connected to ZTNA live feed",
            "timestamp": time.time(),
        }))
        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30)
                if data == "ping":
                    await websocket.send_text(json.dumps({
                        "type": "pong",
                        "timestamp": time.time(),
                    }))
            except asyncio.TimeoutError:
                await websocket.send_text(json.dumps({
                    "type": "heartbeat",
                    "timestamp": time.time(),
                }))
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception:
        ws_manager.disconnect(websocket)
