# backend/websocket_manager.py
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List
import asyncio
import json
import uuid

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.device_scanner = None

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"New WebSocket connection. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        print(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                disconnected.append(connection)
        
        for connection in disconnected:
            self.disconnect(connection)

    async def broadcast_json(self, data: Dict):
        await self.broadcast(json.dumps(data))

# Global WebSocket manager
manager = ConnectionManager()

# WebSocket endpoint for device detection
@app.websocket("/ws/devices")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # Send initial device scan
        from backend.device_detector.device_scanner import DeviceScanner
        scanner = DeviceScanner()
        devices = scanner.detect_connected_devices()
        
        await manager.send_personal_message(json.dumps({
            "type": "device_scan_result",
            "devices": devices
        }), websocket)
        
        # Start auto-detection if requested
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "start_auto_detection":
                await start_auto_device_detection(websocket)
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)

async def start_auto_device_detection(websocket: WebSocket):
    """Start automatic device detection"""
    from backend.device_detector.device_scanner import DeviceScanner
    scanner = DeviceScanner()
    
    previous_devices = []
    
    while True:
        try:
            current_devices = scanner.detect_connected_devices()
            
            # Check for new devices
            for device in current_devices:
                if device not in previous_devices:
                    await manager.send_personal_message(json.dumps({
                        "type": "device_connected",
                        "device": device
                    }), websocket)
            
            # Check for removed devices
            for device in previous_devices:
                if device not in current_devices:
                    await manager.send_personal_message(json.dumps({
                        "type": "device_disconnected", 
                        "device": device
                    }), websocket)
            
            previous_devices = current_devices
            await asyncio.sleep(2)  # Check every 2 seconds
            
        except Exception as e:
            print(f"Auto detection error: {e}")
            await asyncio.sleep(5)
