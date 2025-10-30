# ai-agents/synthetic_intelligence/pattern_recognizer.py
import re
import json
from typing import Dict, List, Any
from collections import defaultdict
import logging

class PatternRecognizer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.email_patterns = self._load_email_patterns()
        self.device_patterns = self._load_device_patterns()
        self.success_patterns = self._load_success_patterns()
    
    def analyze_credential_patterns(self, user_context: Dict) -> List[str]:
        """Analyze user context to generate potential email hypotheses"""
        hypotheses = set()
        
        # Extract basic information
        name = user_context.get('name', '')
        birth_year = user_context.get('birth_year', '')
        previous_emails = user_context.get('known_emails', [])
        common_providers = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com']
        
        # Generate hypotheses based on name patterns
        if name:
            name_parts = name.lower().split()
            if len(name_parts) >= 2:
                first_name, last_name = name_parts[0], name_parts[-1]
                
                # Common email patterns
                patterns = [
                    f"{first_name}.{last_name}",
                    f"{first_name}{last_name}",
                    f"{first_name[0]}{last_name}",
                    f"{first_name}{last_name[0]}",
                    f"{first_name}_{last_name}",
                    f"{last_name}.{first_name}",
                    f"{first_name}",
                    f"{last_name}"
                ]
                
                # Add birth year variations
                if birth_year:
                    year_short = birth_year[-2:]
                    for pattern in patterns[:]:
                        patterns.extend([
                            f"{pattern}{birth_year}",
                            f"{pattern}{year_short}",
                            f"{pattern}_{birth_year}",
                            f"{birth_year}{pattern}"
                        ])
                
                # Generate full email addresses
                for pattern in patterns:
                    for provider in common_providers:
                        hypotheses.add(f"{pattern}@{provider}")
        
        # Learn from previous successful patterns
        learned_patterns = self._get_learned_email_patterns()
        for pattern in learned_patterns:
            if self._pattern_matches_context(pattern, user_context):
                hypotheses.update(self._apply_learned_pattern(pattern, user_context))
        
        return list(hypotheses)[:20]  # Return top 20 hypotheses
    
    def analyze_device_success_patterns(self, device_info: Dict, method: str) -> Dict[str, Any]:
        """Analyze which methods work best for specific devices"""
        device_model = device_info.get('model', '')
        android_version = device_info.get('android_version', '')
        
        # Look for patterns in successful recoveries
        patterns = {
            'samsung_a_series': {
                'pattern': r'SM-A[0-9]',
                'successful_methods': ['combination_firmware', 'emergency_dialer', 'safe_mode']
            },
            'huawei_newer': {
                'pattern': r'^HUAWEI.*ANDROID [8-9]',
                'successful_methods': ['test_point', 'dc_unlocker', 'huawei_multi_tool']
            },
            'oppo_modern': {
                'pattern': r'OPPO.*COLOROS',
                'successful_methods': ['deep_test_mode', 'maui_meta', 'auth_bypass']
            }
        }
        
        for pattern_name, pattern_info in patterns.items():
            if re.search(pattern_info['pattern'], f"{device_model} {android_version}"):
                return {
                    'matched_pattern': pattern_name,
                    'recommended_methods': pattern_info['successful_methods'],
                    'confidence': 0.85
                }
        
        return {'matched_pattern': None, 'recommended_methods': [], 'confidence': 0.0}
