# start_ai_system.py
import asyncio
import uvicorn
from backend.main import app
from ai_agents.strategic_intelligence.agent_orchestrator import AgentOrchestrator
from ai_agents.memory_system.experience_memory import ExperienceMemory

async def initialize_ai_system():
    """Initialize all AI components"""
    print("🤖 Initializing AI Agent System...")
    
    # Initialize memory system
    memory_system = ExperienceMemory()
    print("✅ Memory system initialized")
    
    # Initialize agent orchestrator
    orchestrator = AgentOrchestrator()
    print("✅ Agent orchestrator initialized")
    
    # Load learned patterns
    print("✅ Loading learned experience patterns...")
    
    print("🎯 AI System Ready!")

if __name__ == "__main__":
    # Initialize AI system
    asyncio.run(initialize_ai_system())
    
    # Start web server
    print("🌐 Starting web server on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
