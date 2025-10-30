# backend/main.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict
import asyncio

app = FastAPI(title="Phone Recovery Toolkit")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DeviceScanRequest(BaseModel):
    force_rescan: bool = False

class RecoveryTaskRequest(BaseModel):
    device_info: Dict
    issue_type: str

@app.post("/api/devices/scan")
async def scan_devices(request: DeviceScanRequest):
    from device_detector.device_scanner import DeviceScanner
    scanner = DeviceScanner()
    devices = scanner.detect_connected_devices()
    return devices

@app.post("/api/ai/analyze")
async def analyze_issue(request: RecoveryTaskRequest):
    from ai_coordinator.task_manager import AICoordinator
    coordinator = AICoordinator()
    
    task = await coordinator.create_recovery_plan(
        request.device_info, 
        request.issue_type
    )
    
    return {
        "task_id": task.id,
        "summary": f"AI analysis for {request.issue_type}",
        "steps": task.steps
    }

@app.websocket("/ws/task-progress/{task_id}")
async def websocket_task_progress(websocket: WebSocket, task_id: str):
    await websocket.accept()
    try:
        while True:
            # Send progress updates
            progress_data = {
                "task_id": task_id,
                "progress": 50,
                "current_step": "Processing...",
                "status": "running"
            }
            await websocket.send_json(progress_data)
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        print("Client disconnected")

# Mount static files for frontend
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
