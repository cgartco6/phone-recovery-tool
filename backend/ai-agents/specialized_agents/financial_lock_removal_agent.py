# ai-agents/specialized_agents/financial_lock_removal_agent.py
import asyncio
import subprocess
from typing import Dict, List, Any
import logging

class FinancialLockRemovalAgent:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.payjoy_methods = self._load_payjoy_methods()
        self.payat_methods = self._load_payat_methods()
    
    async def remove_financial_lock(self, device_info: Dict, lock_type: str, context: Dict) -> Dict[str, Any]:
        """Remove financial locks like PayJoy, Pay@, etc."""
        if lock_type.lower() == "payjoy":
            return await self._remove_payjoy_lock(device_info, context)
        elif lock_type.lower() == "pay@":
            return await self._remove_payat_lock(device_info, context)
        else:
            return {"success": False, "error": f"Unsupported financial lock: {lock_type}"}
    
    async def _remove_payjoy_lock(self, device_info: Dict, context: Dict) -> Dict[str, Any]:
        """Remove PayJoy financial lock"""
        try:
            # Detect PayJoy version and method
            payjoy_version = await self._detect_payjoy_version(device_info)
            
            if payjoy_version == "system_app":
                return await self._remove_payjoy_system_app(device_info)
            elif payjoy_version == "boot_lock":
                return await self._remove_payjoy_boot_lock(device_info)
            elif payjoy_version == "persistent":
                return await self._remove_payjoy_persistent(device_info)
            else:
                return {"success": False, "error": "Unknown PayJoy version"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _remove_payjoy_system_app(self, device_info: Dict) -> Dict[str, Any]:
        """Remove PayJoy system app method"""
        try:
            # Gain root access
            if not await self._check_root_access(device_info):
                await self._gain_root_access(device_info)
            
            # Mount system as writable
            await self._mount_system_rw(device_info)
            
            # Remove PayJoy packages
            payjoy_packages = [
                "com.payjoy",
                "com.payjoy.controller",
                "com.payjoy.settings",
                "com.payjoy.app"
            ]
            
            for package in payjoy_packages:
                await self._remove_system_package(device_info, package)
            
            # Remove PayJoy from system partitions
            await self._remove_payjoy_system_files(device_info)
            
            # Clear any PayJoy data
            await self._clear_payjoy_data(device_info)
            
            # Reboot device
            await self._reboot_device(device_info)
            
            return {"success": True, "method": "payjoy_system_removal"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _remove_payat_lock(self, device_info: Dict) -> Dict[str, Any]:
        """Remove Pay@ financial lock"""
        try:
            # Similar approach but Pay@ specific
            await self._mount_system_rw(device_info)
            
            # Pay@ specific packages
            payat_packages = [
                "com.financial.payat",
                "com.payat.controller",
                "com.payat.service"
            ]
            
            for package in payat_packages:
                await self._remove_system_package(device_info, package)
            
            # Additional Pay@ specific cleanup
            await self._clean_payat_residue(device_info)
            
            await self._reboot_device(device_info)
            
            return {"success": True, "method": "payat_removal"}
        except Exception as e:
            return {"success": False, "error": str(e)}
