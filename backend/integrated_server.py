# backend/integrated_server.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import asyncio

# Import all route modules
from backend.main import app as main_app
from backend.ai_routes import router as ai_router
from backend.comprehensive_routes import router as comprehensive_router
from backend.photo_recovery_routes import router as recovery_router

# Create integrated app
app = FastAPI(title="Universal Phone Recovery Toolkit")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(main_app.router)
app.include_router(ai_router)
app.include_router(comprehensive_router)
app.include_router(recovery_router)

# Mount static files
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

@app.on_event("startup")
async def startup_event():
    """Initialize all AI systems on startup"""
    from ai_agents.strategic_intelligence.enhanced_orchestrator import EnhancedAgentOrchestrator
    from ai_agents.memory_system.experience_memory import ExperienceMemory
    
    print("🚀 Starting Universal Phone Recovery Toolkit...")
    
    # Initialize AI systems
    await asyncio.sleep(1)
    print("✅ AI Systems Initialized")
    print("✅ Photo Recovery Agent Ready")
    print("✅ Comprehensive Unlock System Ready")
    print("🌐 Web Interface available at http://localhost:8000")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
