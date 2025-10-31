# backend/ai_agents/synthetic_intelligence/adaptive_learner.py
import json
import logging
from typing import Dict, List, Any
from datetime import datetime, timedelta
import numpy as np
from collections import defaultdict

class AdaptiveLearner:
    def __init__(self, storage_path: str = "learning_data/"):
        self.logger = logging.getLogger(__name__)
        self.storage_path = storage_path
        self.success_patterns = self._load_learning_data('success_patterns')
        self.failure_patterns = self._load_learning_data('failure_patterns')
        self.device_methods = self._load_learning_data('device_methods')
        
    def learn_from_operation(self, device_info: Dict, operation: str, 
                           method: str, success: bool, context: Dict):
        """Learn from each operation to improve future recommendations"""
        learning_entry = {
            'timestamp': datetime.now().isoformat(),
            'device_info': device_info,
            'operation': operation,
            'method': method,
            'success': success,
            'context': context,
            'device_hash': self._hash_device_info(device_info)
        }
        
        if success:
            self.success_patterns.append(learning_entry)
            self._update_success_rates(device_info, method, operation)
        else:
            self.failure_patterns.append(learning_entry)
            self._update_failure_rates(device_info, method, operation)
        
        # Save learning data
        self._save_learning_data()
        
        # Prune old entries (keep last 1000)
        self._prune_old_entries()
    
    def get_recommended_method(self, device_info: Dict, operation: str) -> Dict[str, Any]:
        """Get recommended method based on learned patterns"""
        device_hash = self._hash_device_info(device_info)
        device_family = self._identify_device_family(device_info)
        
        # Look for successful methods for similar devices
        similar_successes = self._find_similar_successes(device_info, operation)
        
        if similar_successes:
            # Use the most successful method for similar devices
            best_method = max(similar_successes, key=lambda x: x['success_rate'])
            return {
                'method': best_method['method'],
                'confidence': best_method['success_rate'],
                'reasoning': f"High success rate ({best_method['success_rate']:.0%}) on similar devices",
                'similar_devices': best_method['device_count']
            }
        
        # Fallback to device family patterns
        family_methods = self._get_family_methods(device_family, operation)
        if family_methods:
            return {
                'method': family_methods[0]['method'],
                'confidence': family_methods[0]['success_rate'],
                'reasoning': f"Common method for {device_family} devices",
                'similar_devices': 'family_pattern'
            }
        
        # Final fallback
        return {
            'method': 'emergency_dialer',
            'confidence': 0.3,
            'reasoning': 'Universal fallback method',
            'similar_devices': 0
        }
    
    def _find_similar_successes(self, device_info: Dict, operation: str) -> List[Dict]:
        """Find successful methods for similar devices"""
        similar_devices = []
        target_family = self._identify_device_family(device_info)
        target_vendor = device_info.get('vendor', '').lower()
        
        # Group successes by method
        method_successes = defaultdict(lambda: {'success_count': 0, 'total_count': 0, 'devices': set()})
        
        for success in self.success_patterns:
            if success['operation'] != operation:
                continue
            
            success_device = success['device_info']
            success_family = self._identify_device_family(success_device)
            success_vendor = success_device.get('vendor', '').lower()
            
            # Check similarity
            similarity_score = self._calculate_device_similarity(
                device_info, success_device, target_family, success_family, target_vendor, success_vendor
            )
            
            if similarity_score > 0.6:  # Similar enough
                method = success['method']
                method_successes[method]['success_count'] += 1
                method_successes[method]['total_count'] += 1
                method_successes[method]['devices'].add(success['device_hash'])
        
        # Also consider failures to calculate success rate
        for failure in self.failure_patterns:
            if failure['operation'] != operation:
                continue
            
            failure_device = failure['device_info']
            failure_family = self._identify_device_family(failure_device)
            failure_vendor = failure_device.get('vendor', '').lower()
            
            similarity_score = self._calculate_device_similarity(
                device_info, failure_device, target_family, failure_family, target_vendor, failure_vendor
            )
            
            if similarity_score > 0.6:
                method = failure['method']
                method_successes[method]['total_count'] += 1
        
        # Calculate success rates
        results = []
        for method, stats in method_successes.items():
            if stats['total_count'] >= 3:  # Minimum sample size
                success_rate = stats['success_count'] / stats['total_count']
                results.append({
                    'method': method,
                    'success_rate': success_rate,
                    'device_count': len(stats['devices']),
                    'total_attempts': stats['total_count']
                })
        
        return results
    
    def _calculate_device_similarity(self, device1: Dict, device2: Dict, 
                                   family1: str, family2: str, vendor1: str, vendor2: str) -> float:
        """Calculate similarity between two devices"""
        similarity = 0.0
        
        # Vendor similarity
        if vendor1 == vendor2:
            similarity += 0.3
        
        # Family similarity
        if family1 == family2:
            similarity += 0.4
        elif family1.split()[0] == family2.split()[0]:  # Same brand
            similarity += 0.2
        
        # Model pattern similarity
        model1 = device1.get('model', '').upper()
        model2 = device2.get('model', '').upper()
        
        if model1 and model2:
            # Check if models share common prefixes
            common_prefix = 0
            for i in range(min(len(model1), len(model2))):
                if model1[i] == model2[i]:
                    common_prefix += 1
                else:
                    break
            
            model_similarity = common_prefix / max(len(model1), len(model2))
            similarity += model_similarity * 0.3
        
        return min(similarity, 1.0)
    
    def _identify_device_family(self, device_info: Dict) -> str:
        """Identify device family from device info"""
        model = device_info.get('model', '').upper()
        vendor = device_info.get('vendor', '').lower()
        
        if 'samsung' in vendor:
            if model.startswith('SM-A'):
                return 'Samsung A Series'
            elif model.startswith('SM-G'):
                return 'Samsung S Series'
        elif 'xiaomi' in vendor:
            if 'REDMI NOTE' in model:
                return 'Xiaomi Redmi Note Series'
        
        return 'Unknown'
    
    def _hash_device_info(self, device_info: Dict) -> str:
        """Create a hash for device info for tracking"""
        import hashlib
        device_str = f"{device_info.get('vendor', '')}_{device_info.get('model', '')}"
        return hashlib.md5(device_str.encode()).hexdigest()
    
    def _load_learning_data(self, data_type: str) -> List:
        """Load learning data from storage"""
        try:
            # In production, this would load from a database
            return []
        except Exception as e:
            self.logger.warning(f"Could not load {data_type}: {e}")
            return []
    
    def _save_learning_data(self):
        """Save learning data to storage"""
        try:
            # In production, this would save to a database
            pass
        except Exception as e:
            self.logger.error(f"Failed to save learning data: {e}")
    
    def _prune_old_entries(self):
        """Remove old entries to prevent memory issues"""
        max_entries = 1000
        if len(self.success_patterns) > max_entries:
            self.success_patterns = self.success_patterns[-max_entries:]
        if len(self.failure_patterns) > max_entries:
            self.failure_patterns = self.failure_patterns[-max_entries:]
