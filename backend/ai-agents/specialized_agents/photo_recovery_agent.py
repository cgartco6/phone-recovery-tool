# ai-agents/specialized_agents/photo_recovery_agent.py
import asyncio
import os
import subprocess
from typing import Dict, List, Any
from dataclasses import dataclass
import logging
import shutil
from pathlib import Path

@dataclass
class RecoveryResult:
    total_files_found: int
    photos_recovered: int
    videos_recovered: int
    documents_recovered: int
    recovered_size: int
    recovery_path: str

class PhotoRecoveryAgent:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.recovery_methods = self._load_recovery_methods()
        self.supported_formats = {
            'photos': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.heic', '.raw'],
            'videos': ['.mp4', '.avi', '.mov', '.mkv', '.3gp', '.wmv', '.flv'],
            'documents': ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt']
        }
    
    async def recover_media_before_reset(self, device_info: Dict, context: Dict) -> RecoveryResult:
        """Comprehensive media recovery before any reset operations"""
        try:
            # Analyze device storage and recovery options
            storage_analysis = await self._analyze_device_storage(device_info)
            
            # Determine recovery method based on device state
            recovery_method = await self._select_recovery_method(device_info, storage_analysis)
            
            # Create recovery directory
            recovery_dir = await self._create_recovery_directory(device_info)
            
            # Execute recovery
            recovery_result = await self._execute_recovery(
                recovery_method, device_info, recovery_dir, storage_analysis
            )
            
            # Backup recovery results
            await self._backup_recovery_metadata(recovery_result, device_info)
            
            return recovery_result
            
        except Exception as e:
            self.logger.error(f"Photo recovery failed: {e}")
            return RecoveryResult(0, 0, 0, 0, 0, "")
    
    async def _analyze_device_storage(self, device_info: Dict) -> Dict[str, Any]:
        """Analyze device storage for recoverable media"""
        storage_info = {}
        
        try:
            # Check if ADB is accessible
            if await self._check_adb_access(device_info):
                # Get storage paths
                storage_paths = await self._get_storage_paths(device_info)
                
                for path in storage_paths:
                    # Analyze each storage path for media files
                    path_analysis = await self._analyze_storage_path(device_info, path)
                    storage_info[path] = path_analysis
            
            # Estimate recoverable data based on device model and usage
            storage_info['recovery_estimate'] = await self._estimate_recoverable_data(device_info)
            
            return storage_info
            
        except Exception as e:
            self.logger.error(f"Storage analysis failed: {e}")
            return {}
    
    async def _select_recovery_method(self, device_info: Dict, storage_analysis: Dict) -> str:
        """Select the most appropriate recovery method"""
        device_state = await self._determine_device_state(device_info)
        
        if device_state == "normal":
            return "adb_pull"
        elif device_state == "recovery":
            return "recovery_mode"
        elif device_state == "fastboot":
            return "fastboot_dump"
        elif "locked" in device_state:
            return "advanced_recovery"
        else:
            return "comprehensive_scan"
    
    async def _execute_recovery(self, method: str, device_info: Dict, recovery_dir: str, storage_analysis: Dict) -> RecoveryResult:
        """Execute the selected recovery method"""
        if method == "adb_pull":
            return await self._adb_pull_recovery(device_info, recovery_dir)
        elif method == "recovery_mode":
            return await self._recovery_mode_backup(device_info, recovery_dir)
        elif method == "fastboot_dump":
            return await self._fastboot_dump_recovery(device_info, recovery_dir)
        elif method == "advanced_recovery":
            return await self._advanced_recovery_scan(device_info, recovery_dir)
        else:
            return await self._comprehensive_recovery_scan(device_info, recovery_dir)
    
    async def _adb_pull_recovery(self, device_info: Dict, recovery_dir: str) -> RecoveryResult:
        """Recover media using ADB pull commands"""
        recovered_files = 0
        recovered_size = 0
        photos = 0
        videos = 0
        documents = 0
        
        try:
            # Common media directories on Android
            media_directories = [
                "/sdcard/DCIM/Camera",
                "/sdcard/DCIM/Screenshots", 
                "/sdcard/Pictures",
                "/sdcard/Download",
                "/sdcard/Movies",
                "/sdcard/WhatsApp/Media",
                "/sdcard/Telegram",
                "/sdcard/Messenger",
                "/sdcard/Instagram"
            ]
            
            for directory in media_directories:
                try:
                    # Check if directory exists
                    check_cmd = f"adb shell \"ls {directory}\""
                    result = subprocess.run(check_cmd, shell=True, capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        # Directory exists, pull files
                        pull_cmd = f"adb pull \"{directory}\" \"{recovery_dir}/$(basename {directory})\""
                        subprocess.run(pull_cmd, shell=True, capture_output=True)
                        
                        # Count recovered files
                        dir_path = Path(recovery_dir) / Path(directory).name
                        if dir_path.exists():
                            for file_type, extensions in self.supported_formats.items():
                                for ext in extensions:
                                    files = list(dir_path.rglob(f"*{ext}"))
                                    files.extend(list(dir_path.rglob(f"*{ext.upper()}")))
                                    
                                    if file_type == 'photos':
                                        photos += len(files)
                                    elif file_type == 'videos':
                                        videos += len(files)
                                    elif file_type == 'documents':
                                        documents += len(files)
                                    
                                    recovered_files += len(files)
                                    recovered_size += sum(f.stat().st_size for f in files if f.is_file())
                
                except Exception as e:
                    self.logger.warning(f"Failed to recover from {directory}: {e}")
                    continue
            
            return RecoveryResult(
                total_files_found=recovered_files,
                photos_recovered=photos,
                videos_recovered=videos, 
                documents_recovered=documents,
                recovered_size=recovered_size,
                recovery_path=recovery_dir
            )
            
        except Exception as e:
            self.logger.error(f"ADB pull recovery failed: {e}")
            return RecoveryResult(0, 0, 0, 0, 0, recovery_dir)
    
    async def _advanced_recovery_scan(self, device_info: Dict, recovery_dir: str) -> RecoveryResult:
        """Advanced recovery using forensic techniques"""
        try:
            # Use various recovery tools based on device state
            recovery_tools = [
                "adb shell ls -la /sdcard/",
                "adb shell find /sdcard -name '*.jpg' -o -name '*.mp4' -o -name '*.png'",
                "adb shell du -h /sdcard/DCIM/",
            ]
            
            recovered_files = 0
            recovered_size = 0
            
            # Try to access deleted files through data recovery apps
            recovery_apps = [
                "com.diskdigger",
                "com.photos.recovery", 
                "com.defianttech.diskdigger"
            ]
            
            for app in recovery_apps:
                try:
                    # Check if recovery app is installed
                    check_cmd = f"adb shell pm list packages {app}"
                    result = subprocess.run(check_cmd, shell=True, capture_output=True, text=True)
                    
                    if app in result.stdout:
                        # Launch recovery app
                        launch_cmd = f"adb shell am start -n {app}/.MainActivity"
                        subprocess.run(launch_cmd, shell=True)
                        
                        # Wait for recovery to complete
                        await asyncio.sleep(10)
                        
                        # Pull recovered files
                        app_data_cmd = f"adb pull /sdcard/diskdigger_pics {recovery_dir}/diskdigger"
                        subprocess.run(app_data_cmd, shell=True)
                
                except Exception as e:
                    continue
            
            # Count recovered files
            recovery_path = Path(recovery_dir)
            if recovery_path.exists():
                for file_type, extensions in self.supported_formats.items():
                    for ext in extensions:
                        files = list(recovery_path.rglob(f"*{ext}"))
                        files.extend(list(recovery_path.rglob(f"*{ext.upper()}")))
                        recovered_files += len(files)
                        recovered_size += sum(f.stat().st_size for f in files if f.is_file())
            
            return RecoveryResult(
                total_files_found=recovered_files,
                photos_recovered=recovered_files,  # Simplified count
                videos_recovered=0,
                documents_recovered=0,
                recovered_size=recovered_size,
                recovery_path=recovery_dir
            )
            
        except Exception as e:
            self.logger.error(f"Advanced recovery failed: {e}")
            return RecoveryResult(0, 0, 0, 0, 0, recovery_dir)
