# backend/ai_routes.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List

router = APIRouter()

class CredentialAnalysisRequest(BaseModel):
    clues: str
    context: Dict[str, Any]

class TaskPlanRequest(BaseModel):
    device_info: Dict[str, Any]
    issue: str
    context: Dict[str, Any]

@router.post("/api/ai/analyze-credentials")
async def analyze_credentials(request: CredentialAnalysisRequest):
    from ai_agents.specialized_agents.credential_recovery_agent import CredentialRecoveryAgent
    from ai_agents.synthetic_intelligence.pattern_recognizer import PatternRecognizer
    
    try:
        # Extract user context from clues
        pattern_recognizer = PatternRecognizer()
        user_context = pattern_recognizer.extract_user_context(request.clues)
        user_context.update(request.context)
        
        # Generate email hypotheses
        credential_agent = CredentialRecoveryAgent()
        hypotheses = await credential_agent.recover_possible_emails(user_context)
        
        return {
            "hypotheses": [
                {
                    "email": h.email,
                    "confidence": h.confidence,
                    "reasoning": h.reasoning,
                    "verification_status": h.verification_status
                }
                for h in hypotheses
            ],
            "user_context": user_context
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/ai/create-task-plan")
async def create_task_plan(request: TaskPlanRequest):
    from ai_agents.strategic_intelligence.task_decomposer import TaskDecomposer
    from ai_agents.strategic_intelligence.agent_orchestrator import AgentOrchestrator
    
    try:
        decomposer = TaskDecomposer()
        subtasks = decomposer.decompose_task(
            request.issue, 
            request.device_info, 
            request.context
        )
        
        return {
            "complexity": "complex",  # This would be calculated
            "subtasks": [
                {
                    "id": task.id,
                    "description": task.description,
                    "dependencies": task.dependencies,
                    "agent_type": task.agent_type,
                    "estimated_duration": task.estimated_duration,
                    "required_tools": task.required_tools
                }
                for task in subtasks
            ],
            "estimated_total_time": sum(task.estimated_duration for task in subtasks)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/ai/agent-status")
async def get_agent_status():
    from ai_agents.strategic_intelligence.agent_orchestrator import AgentOrchestrator
    
    orchestrator = AgentOrchestrator()
    status = {
        agent_id: {
            "name": agent.name,
            "status": agent.status.value,
            "current_task": agent.current_task,
            "capabilities": agent.capabilities
        }
        for agent_id, agent in orchestrator.agents.items()
    }
    
    return status
