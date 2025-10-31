# backend/main.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import uvicorn
import asyncio
import os

app = FastAPI(title="Universal Phone Recovery Toolkit")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include all routers
from backend.ai_routes import router as ai_router
from backend.comprehensive_routes import router as comprehensive_router
from backend.photo_recovery_routes import router as recovery_router
from backend.websocket_manager import manager, websocket_endpoint

app.include_router(ai_router)
app.include_router(comprehensive_router)
app.include_router(recovery_router)
app.websocket("/ws/devices")(websocket_endpoint)

# Serve static files
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
app.mount("/js", StaticFiles(directory="frontend/src/js"), name="js")

@app.get("/")
async def read_index():
    return FileResponse('frontend/index.html')

@app.get("/api/devices/scan")
async def scan_devices():
    from backend.device_detector.device_scanner import DeviceScanner
    try:
        scanner = DeviceScanner()
        devices = scanner.detect_connected_devices()
        return devices
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/drivers/install")
async def install_drivers(request: dict):
    from backend.driver_software_manager.universal_driver_manager import UniversalDriverManager
    try:
        driver_manager = UniversalDriverManager()
        result = await driver_manager.install_required_drivers(request.get('device_info', {}))
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.on_event("startup")
async def startup_event():
    """Initialize all systems on startup"""
    print("🚀 Starting Universal Phone Recovery Toolkit...")
    
    # Initialize AI systems
    try:
        from ai_agents.strategic_intelligence.enhanced_orchestrator import EnhancedAgentOrchestrator
        from ai_agents.memory_system.experience_memory import ExperienceMemory
        
        # Initialize in background
        asyncio.create_task(initialize_ai_systems())
        
        print("✅ Backend systems initialized")
        print("✅ WebSocket server ready")
        print("✅ Device detection active")
        print("🌐 Web Interface: http://localhost:8000")
        
    except Exception as e:
        print(f"❌ Startup error: {e}")

async def initialize_ai_systems():
    """Initialize AI systems in background"""
    try:
        from ai_agents.strategic_intelligence.enhanced_orchestrator import EnhancedAgentOrchestrator
        from ai_agents.memory_system.experience_memory import ExperienceMemory
        
        # Initialize orchestrator
        orchestrator = EnhancedAgentOrchestrator()
        memory_system = ExperienceMemory()
        
        print("✅ AI Agent System Initialized")
        print("✅ Strategic Intelligence Ready")
        print("✅ Photo Recovery Agent Online")
        print("✅ All Removal Agents Active")
        
    except Exception as e:
        print(f"❌ AI System initialization failed: {e}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
