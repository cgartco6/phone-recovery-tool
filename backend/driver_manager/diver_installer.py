# backend/driver_manager/driver_installer.py
import requests
import os
import zipfile
import hashlib

class DriverManager:
    def __init__(self):
        self.driver_db = {
            "samsung": {
                "url": "https://developer.samsung.com/android-usb-driver",
                "filename": "samsung_usb_driver.zip",
                "checksum": "abc123..."
            },
            "huawei": {
                "url": "https://developer.huawei.com/consumer/en/doc/development/",
                "filename": "huawei_driver.zip",
                "checksum": "def456..."
            }
        }
    
    def install_drivers(self, device_info: Dict) -> bool:
        vendor = device_info['vendor'].lower()
        
        if vendor not in self.driver_db:
            return self._generic_driver_install(device_info)
        
        driver_info = self.driver_db[vendor]
        return self._download_and_install(driver_info)
    
    def _download_and_install(self, driver_info: Dict) -> bool:
        try:
            # Download driver
            response = requests.get(driver_info['url'], stream=True)
            temp_path = f"/tmp/{driver_info['filename']}"
            
            with open(temp_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Verify checksum
            if self._verify_checksum(temp_path, driver_info['checksum']):
                # Extract and install
                with zipfile.ZipFile(temp_path, 'r') as zip_ref:
                    zip_ref.extractall("/drivers/")
                return True
        except Exception as e:
            print(f"Driver installation failed: {e}")
            return False
    
    def _verify_checksum(self, file_path: str, expected_checksum: str) -> bool:
        with open(file_path, 'rb') as f:
            file_hash = hashlib.md5()
            while chunk := f.read(8192):
                file_hash.update(chunk)
            return file_hash.hexdigest() == expected_checksum
