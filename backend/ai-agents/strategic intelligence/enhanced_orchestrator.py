# ai-agents/strategic_intelligence/enhanced_orchestrator.py
import asyncio
from typing import Dict, List, Any
from dataclasses import dataclass
import uuid

class EnhancedAgentOrchestrator:
    def __init__(self):
        self.agents = {}
        self.driver_manager = UniversalDriverManager()
        self.manufacturer_agent = ManufacturerIntelligenceAgent()
        self._initialize_all_agents()
    
    def _initialize_all_agents(self):
        """Initialize all specialized removal agents"""
        from ai_agents.specialized_agents.frp_removal_agent import FRPRemovalAgent
        from ai_agents.specialized_agents.kg_removal_agent import KGRemovalAgent
        from ai_agents.specialized_agents.mdm_removal_agent import MDMRemovalAgent
        from ai_agents.specialized_agents.google_account_removal_agent import GoogleAccountRemovalAgent
        from ai_agents.specialized_agents.financial_lock_removal_agent import FinancialLockRemovalAgent
        
        self.agents = {
            "frp_agent": FRPRemovalAgent(),
            "kg_agent": KGRemovalAgent(),
            "mdm_agent": MDMRemovalAgent(),
            "google_account_agent": GoogleAccountRemovalAgent(),
            "financial_lock_agent": FinancialLockRemovalAgent(),
            "diagnostic_agent": DiagnosticAgent(),
            "firmware_agent": FirmwareManagementAgent()
        }
    
    async def comprehensive_unlock_device(self, device_info: Dict, issues: List[str]) -> Dict[str, Any]:
        """Comprehensive device unlocking handling multiple issues"""
        results = {}
        
        # First, analyze device thoroughly
        device_analysis = await self.manufacturer_agent.analyze_device(device_info)
        results['device_analysis'] = device_analysis
        
        # Install required drivers and software
        driver_result = await self.driver_manager.install_required_drivers(device_info)
        results['driver_installation'] = driver_result
        
        # Process each issue in optimal order
        processing_order = self._determine_processing_order(issues)
        
        for issue in processing_order:
            issue_result = await self._process_single_issue(issue, device_info, device_analysis)
            results[issue] = issue_result
            
            # If critical issue fails, stop processing
            if issue in ['frp', 'kg_lock'] and not issue_result.get('success'):
                results['overall_success'] = False
                results['failed_on'] = issue
                break
        
        results['overall_success'] = all(
            results.get(issue, {}).get('success', False) 
            for issue in issues
        )
        
        return results
    
    async def _process_single_issue(self, issue: str, device_info: Dict, analysis: Dict) -> Dict[str, Any]:
        """Process a single device issue with appropriate agent"""
        if issue == 'frp':
            return await self.agents['frp_agent'].remove_frp_lock(device_info, analysis)
        elif issue == 'kg_lock':
            return await self.agents['kg_agent'].remove_kg_lock(device_info, analysis)
        elif issue == 'mdm':
            return await self.agents['mdm_agent'].remove_mdm_lock(device_info, analysis)
        elif issue == 'google_account':
            return await self.agents['google_account_agent'].remove_google_account(device_info, analysis)
        elif issue in ['payjoy', 'pay@']:
            return await self.agents['financial_lock_agent'].remove_financial_lock(device_info, issue, analysis)
        else:
            return {"success": False, "error": f"Unsupported issue: {issue}"}
    
    def _determine_processing_order(self, issues: List[str]) -> List[str]:
        """Determine optimal processing order for issues"""
        priority_order = ['kg_lock', 'mdm', 'frp', 'google_account', 'payjoy', 'pay@']
        
        # Sort issues by priority
        sorted_issues = []
        for priority_issue in priority_order:
            if priority_issue in issues:
                sorted_issues.append(priority_issue)
        
        # Add any remaining issues not in priority list
        for issue in issues:
            if issue not in sorted_issues:
                sorted_issues.append(issue)
        
        return sorted_issues
