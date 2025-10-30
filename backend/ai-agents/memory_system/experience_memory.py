# ai-agents/memory_system/experience_memory.py
import json
import pickle
from typing import Dict, List, Any
from datetime import datetime
import numpy as np
from collections import defaultdict

class ExperienceMemory:
    def __init__(self, storage_path: str = "memory/"):
        self.storage_path = storage_path
        self.successful_recoveries = self._load_memory('successful_recoveries')
        self.failed_attempts = self._load_memory('failed_attempts')
        self.device_patterns = self._load_memory('device_patterns')
        self.email_patterns = self._load_memory('email_patterns')
    
    def record_success(self, device_info: Dict, method: str, steps: List[str], context: Dict):
        """Record a successful recovery for future learning"""
        recovery_id = f"{device_info.get('model', 'unknown')}_{datetime.now().timestamp()}"
        
        success_record = {
            'id': recovery_id,
            'timestamp': datetime.now().isoformat(),
            'device_info': device_info,
            'method_used': method,
            'steps_taken': steps,
            'context': context,
            'success_factors': self._extract_success_factors(device_info, method, context)
        }
        
        self.successful_recoveries[recovery_id] = success_record
        self._update_device_patterns(device_info, method, True)
        self._save_memory('successful_recoveries', self.successful_recoveries)
    
    def record_failure(self, device_info: Dict, method: str, error: str, context: Dict):
        """Record a failed attempt for learning"""
        failure_id = f"failed_{device_info.get('model', 'unknown')}_{datetime.now().timestamp()}"
        
        failure_record = {
            'id': failure_id,
            'timestamp': datetime.now().isoformat(),
            'device_info': device_info,
            'method_attempted': method,
            'error': error,
            'context': context
        }
        
        self.failed_attempts[failure_id] = failure_record
        self._update_device_patterns(device_info, method, False)
        self._save_memory('failed_attempts', self.failed_attempts)
    
    def get_similar_successes(self, device_info: Dict) -> List[Dict]:
        """Find similar successful recoveries for current device"""
        similar = []
        device_model = device_info.get('model', '').lower()
        android_version = device_info.get('android_version', '')
        
        for recovery_id, recovery in self.successful_recoveries.items():
            rec_device = recovery['device_info']
            rec_model = rec_device.get('model', '').lower()
            
            # Simple similarity check (can be enhanced with ML)
            if (device_model in rec_model or rec_model in device_model) and \
               rec_device.get('vendor') == device_info.get('vendor'):
                similar.append(recovery)
        
        return sorted(similar, key=lambda x: x['timestamp'], reverse=True)[:5]
    
    def _extract_success_factors(self, device_info: Dict, method: str, context: Dict) -> Dict[str, Any]:
        """Extract factors that contributed to success"""
        return {
            'device_family': self._categorize_device(device_info),
            'android_version_range': self._get_version_range(device_info.get('android_version')),
            'method_category': self._categorize_method(method),
            'tools_used': context.get('tools_used', []),
            'time_taken': context.get('time_taken', 0),
            'prerequisites': context.get('prerequisites', [])
        }
