# backend/ai_agents/synthetic_intelligence/pattern_recognizer.py
import re
import json
import logging
from typing import Dict, List, Any, Tuple
from datetime import datetime
import hashlib

class PatternRecognizer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.patterns_db = self._load_patterns_database()
        self.success_patterns = self._load_success_patterns()
        
    def analyze_device_patterns(self, device_info: Dict) -> Dict[str, Any]:
        """Analyze device patterns to predict successful methods"""
        device_model = device_info.get('model', '').upper()
        vendor = device_info.get('vendor', '').lower()
        android_version = device_info.get('android_version', '')
        
        analysis = {
            'device_family': self._identify_device_family(device_model, vendor),
            'chipset_pattern': self._identify_chipset_pattern(device_model),
            'android_pattern': self._analyze_android_pattern(android_version),
            'successful_methods': self._find_successful_methods(device_model, vendor),
            'known_issues': self._get_known_issues(device_model, vendor),
            'recovery_complexity': self._assess_recovery_complexity(device_info)
        }
        
        return analysis
    
    def analyze_credential_patterns(self, user_context: Dict) -> List[Dict[str, Any]]:
        """Analyze user context to generate email hypotheses"""
        hypotheses = []
        
        # Extract user information
        name = user_context.get('name', '')
        birth_year = user_context.get('birth_year', '')
        phone = user_context.get('phone', '')
        location = user_context.get('location', '')
        known_emails = user_context.get('known_emails', [])
        
        # Common email patterns
        email_patterns = self._generate_email_patterns(name, birth_year, phone, location)
        
        for pattern_data in email_patterns:
            confidence = self._calculate_pattern_confidence(pattern_data, user_context)
            
            hypothesis = {
                'email': pattern_data['email'],
                'confidence': confidence,
                'reasoning': pattern_data['reasoning'],
                'pattern_type': pattern_data['type'],
                'verification_status': 'unverified'
            }
            
            hypotheses.append(hypothesis)
        
        # Sort by confidence
        hypotheses.sort(key=lambda x: x['confidence'], reverse=True)
        
        return hypotheses[:10]  # Return top 10 hypotheses
    
    def _generate_email_patterns(self, name: str, birth_year: str, phone: str, location: str) -> List[Dict]:
        """Generate possible email patterns based on user information"""
        patterns = []
        
        if not name:
            return patterns
        
        name_parts = name.lower().split()
        if len(name_parts) < 2:
            return patterns
        
        first_name, last_name = name_parts[0], name_parts[-1]
        
        # Common email providers
        providers = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'icloud.com']
        
        # Base name combinations
        name_combinations = [
            (f"{first_name}.{last_name}", "first.last"),
            (f"{first_name}{last_name}", "firstlast"),
            (f"{first_name[0]}{last_name}", "first_initial_last"),
            (f"{first_name}{last_name[0]}", "first_last_initial"),
            (f"{first_name}_{last_name}", "first_underscore_last"),
            (f"{last_name}.{first_name}", "last.first"),
            (f"{last_name}{first_name}", "lastfirst"),
            (first_name, "first_name_only"),
            (last_name, "last_name_only")
        ]
        
        # Add numerical suffixes
        numerical_patterns = []
        for base, pattern_type in name_combinations:
            numerical_patterns.append((base, pattern_type))
            
            if birth_year:
                numerical_patterns.extend([
                    (f"{base}{birth_year}", f"{pattern_type}_birthyear"),
                    (f"{base}{birth_year[-2:]}", f"{pattern_type}_birthyear_short"),
                    (f"{base}_{birth_year}", f"{pattern_type}_underscore_birthyear")
                ])
            
            # Common numerical suffixes
            numerical_patterns.extend([
                (f"{base}123", f"{pattern_type}_123"),
                (f"{base}1", f"{pattern_type}_1"),
                (f"{base}2", f"{pattern_type}_2")
            ])
        
        # Generate full email addresses
        for pattern, pattern_type in numerical_patterns:
            for provider in providers:
                email = f"{pattern}@{provider}"
                reasoning = f"Based on {pattern_type.replace('_', ' ')} pattern with {provider}"
                
                patterns.append({
                    'email': email,
                    'reasoning': reasoning,
                    'type': pattern_type,
                    'provider': provider
                })
        
        return patterns
    
    def _calculate_pattern_confidence(self, pattern_data: Dict, user_context: Dict) -> float:
        """Calculate confidence score for an email pattern"""
        confidence = 0.5  # Base confidence
        
        # Boost confidence for matching provider with known emails
        known_emails = user_context.get('known_emails', [])
        for known_email in known_emails:
            if '@' in known_email:
                known_provider = known_email.split('@')[1]
                if pattern_data['provider'] == known_provider:
                    confidence += 0.2
                    break
        
        # Boost for having birth year in pattern if available
        if user_context.get('birth_year') and user_context['birth_year'] in pattern_data['email']:
            confidence += 0.15
        
        # Adjust based on pattern type
        pattern_type = pattern_data['type']
        if 'first.last' in pattern_type or 'last.first' in pattern_type:
            confidence += 0.1
        elif 'firstlast' in pattern_type or 'lastfirst' in pattern_type:
            confidence += 0.05
        
        # Cap at 0.95
        return min(confidence, 0.95)
    
    def _identify_device_family(self, model: str, vendor: str) -> str:
        """Identify device family based on model pattern"""
        if 'samsung' in vendor:
            if model.startswith('SM-A'):
                return 'Samsung A Series'
            elif model.startswith('SM-G'):
                return 'Samsung Galaxy S Series'
            elif model.startswith('SM-J'):
                return 'Samsung J Series'
            elif model.startswith('SM-N'):
                return 'Samsung Note Series'
            elif model.startswith('SM-T'):
                return 'Samsung Tablet Series'
        
        elif 'xiaomi' in vendor or 'redmi' in vendor:
            if 'REDMI NOTE' in model:
                return 'Xiaomi Redmi Note Series'
            elif 'REDMI' in model:
                return 'Xiaomi Redmi Series'
            elif 'MI ' in model:
                return 'Xiaomi Mi Series'
            elif 'POCO' in model:
                return 'Xiaomi Poco Series'
        
        elif 'huawei' in vendor:
            if any(x in model for x in ['P', 'MATE', 'NOVA']):
                return 'Huawei Flagship Series'
            elif 'Y' in model:
                return 'Huawei Y Series'
        
        return 'Unknown Family'
    
    def _find_successful_methods(self, model: str, vendor: str) -> List[str]:
        """Find successful methods for similar devices"""
        successful_methods = []
        
        # Pattern-based method prediction
        if 'samsung' in vendor:
            if 'SM-A' in model:
                successful_methods.extend(['combination_firmware', 'odin_flash', 'emergency_dialer'])
            elif 'SM-G' in model:
                successful_methods.extend(['combination_firmware', 'samkey', 'z3x_box'])
        
        elif 'huawei' in vendor:
            successful_methods.extend(['test_point', 'dc_unlocker', 'huawei_multi_tool'])
        
        elif 'xiaomi' in vendor or 'redmi' in vendor:
            successful_methods.extend(['auth_bypass', 'mi_flash_tool', 'sp_flash_tool'])
        
        # Universal methods
        successful_methods.extend(['adb_commands', 'safe_mode', 'factory_reset'])
        
        return successful_methods
    
    def _load_patterns_database(self) -> Dict:
        """Load pattern database from file"""
        try:
            # This would load from a JSON file in production
            return {
                "samsung_patterns": {
                    "A_Series": r"SM-A[0-9]{3,}",
                    "S_Series": r"SM-G[0-9]{3,}",
                    "Note_Series": r"SM-N[0-9]{3,}"
                },
                "email_patterns": {
                    "first_last": r"^[a-z]+\.[a-z]+@",
                    "firstlast": r"^[a-z]+[a-z]+@",
                    "with_numbers": r".*[0-9]+.*@"
                }
            }
        except Exception as e:
            self.logger.error(f"Failed to load patterns database: {e}")
            return {}
    
    def _load_success_patterns(self) -> Dict:
        """Load success patterns from learning data"""
        try:
            # This would load from a database in production
            return {
                "samsung_sm_a": {
                    "frp_success": ["combination_firmware", "emergency_dialer"],
                    "kg_success": ["combination_reset", "efs_repair"]
                },
                "xiaomi_redmi_note": {
                    "frp_success": ["auth_bypass", "mi_tool"],
                    "pattern_success": ["adb_remove", "sqlite_edit"]
                }
            }
        except Exception as e:
            self.logger.error(f"Failed to load success patterns: {e}")
            return {}
