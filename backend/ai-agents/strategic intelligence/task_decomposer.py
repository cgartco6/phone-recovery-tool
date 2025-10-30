# ai-agents/strategic_intelligence/task_decomposer.py
from typing import List, Dict, Any
from dataclasses import dataclass
from enum import Enum
import logging

class TaskComplexity(Enum):
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    VERY_COMPLEX = "very_complex"

@dataclass
class Subtask:
    id: str
    description: str
    dependencies: List[str]
    agent_type: str
    estimated_duration: int
    required_tools: List[str]

class TaskDecomposer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.task_templates = self._load_task_templates()
    
    def decompose_task(self, main_task: str, device_info: Dict, context: Dict) -> List[Subtask]:
        """Break down complex tasks into manageable subtasks"""
        complexity = self._assess_complexity(main_task, device_info)
        
        if "frp" in main_task.lower():
            return self._decompose_frp_task(device_info, context)
        elif "google account" in main_task.lower() or "email" in main_task.lower():
            return self._decompose_credential_recovery_task(device_info, context)
        elif "pattern" in main_task.lower() or "pin" in main_task.lower():
            return self._decompose_lock_removal_task(device_info, context)
        elif "firmware" in main_task.lower():
            return self._decompose_firmware_task(device_info, context)
        else:
            return self._decompose_generic_task(main_task, device_info, context)
    
    def _decompose_frp_task(self, device_info: Dict, context: Dict) -> List[Subtask]:
        """Decompose FRP removal task"""
        subtasks = [
            Subtask(
                id="detect_device",
                description="Identify device model and current state",
                dependencies=[],
                agent_type="diagnostic_agent",
                estimated_duration=30,
                required_tools=["device_detector", "usb_analyzer"]
            ),
            Subtask(
                id="research_methods",
                description="Find applicable FRP bypass methods for this device",
                dependencies=["detect_device"],
                agent_type="research_agent",
                estimated_duration=120,
                required_tools=["web_scraper", "knowledge_base"]
            ),
            Subtask(
                id="prepare_tools",
                description="Download required firmware and tools",
                dependencies=["research_methods"],
                agent_type="firmware_agent",
                estimated_duration=300,
                required_tools=["download_manager", "firmware_library"]
            ),
            Subtask(
                id="execute_bypass",
                description="Perform FRP bypass procedure",
                dependencies=["prepare_tools"],
                agent_type="bypass_agent",
                estimated_duration=600,
                required_tools=["adb", "fastboot", "flashtool"]
            ),
            Subtask(
                id="verify_success",
                description="Confirm FRP is removed and device is functional",
                dependencies=["execute_bypass"],
                agent_type="diagnostic_agent",
                estimated_duration=60,
                required_tools=["device_verifier"]
            )
        ]
        
        # Add device-specific subtasks
        if "samsung" in device_info.get('vendor', '').lower():
            subtasks.insert(3, Subtask(
                id="download_combination",
                description="Download combination firmware for Samsung device",
                dependencies=["research_methods"],
                agent_type="firmware_agent",
                estimated_duration=180,
                required_tools=["samloader", "firmware_downloader"]
            ))
        
        return subtasks
    
    def _decompose_credential_recovery_task(self, device_info: Dict, context: Dict) -> List[Subtask]:
        """Decompose credential recovery task for forgotten emails"""
        return [
            Subtask(
                id="analyze_usage_patterns",
                description="Analyze user behavior and potential email patterns",
                dependencies=[],
                agent_type="credential_agent",
                estimated_duration=60,
                required_tools=["pattern_analyzer"]
            ),
            Subtask(
                id="generate_email_hypotheses",
                description="Generate possible email addresses based on user info",
                dependencies=["analyze_usage_patterns"],
                agent_type="credential_agent",
                estimated_duration=120,
                required_tools=["email_generator", "context_analyzer"]
            ),
            Subtask(
                id="research_recovery_options",
                description="Find account recovery methods for different providers",
                dependencies=["generate_email_hypotheses"],
                agent_type="research_agent",
                estimated_duration=180,
                required_tools=["web_scraper", "recovery_knowledge"]
            ),
            Subtask(
                id="attempt_device_recovery",
                description="Try device-specific credential recovery methods",
                dependencies=["research_recovery_options"],
                agent_type="bypass_agent",
                estimated_duration=300,
                required_tools=["adb", "recovery_tools"]
            ),
            Subtask(
                id="document_findings",
                description="Record successful patterns and methods",
                dependencies=["attempt_device_recovery"],
                agent_type="memory_agent",
                estimated_duration=60,
                required_tools=["knowledge_base"]
            )
        ]
