# backend/comprehensive_routes.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List

router = APIRouter()

class ComprehensiveUnlockRequest(BaseModel):
    device_info: Dict[str, Any]
    issues: List[str]

class DriverInstallRequest(BaseModel):
    device_info: Dict[str, Any]

@router.post("/api/unlock/comprehensive")
async def comprehensive_unlock(request: ComprehensiveUnlockRequest):
    from ai_agents.strategic_intelligence.enhanced_orchestrator import EnhancedAgentOrchestrator
    
    try:
        orchestrator = EnhancedAgentOrchestrator()
        results = await orchestrator.comprehensive_unlock_device(
            request.device_info, 
            request.issues
        )
        
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/drivers/install-all")
async def install_all_drivers(request: DriverInstallRequest):
    from backend.driver_software_manager.universal_driver_manager import UniversalDriverManager
    
    try:
        driver_manager = UniversalDriverManager()
        results = await driver_manager.install_required_drivers(request.device_info)
        
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/software/download-tools")
async def download_tools(request: ComprehensiveUnlockRequest):
    from backend.driver_software_manager.universal_driver_manager import UniversalDriverManager
    
    try:
        driver_manager = UniversalDriverManager()
        results = await driver_manager.download_required_software(
            request.device_info, 
            "comprehensive_unlock"
        )
        
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
