# backend/device_detector/device_scanner.py
import subprocess
import usb.core
import usb.util
import platform
from typing import Dict, List

class DeviceScanner:
    def __init__(self):
        self.supported_vendors = {
            0x04E8: "Samsung",
            0x18D1: "Google",
            0x12D1: "Huawei",
            0x1004: "LG",
            0x22D9: "Oppo",
            0x2A45: "Hisense",
            0x0489: "Honor"
        }
    
    def detect_connected_devices(self) -> List[Dict]:
        devices = []
        system = platform.system()
        
        if system == "Windows":
            devices.extend(self._scan_windows())
        elif system == "Linux":
            devices.extend(self._scan_linux())
        elif system == "Darwin":
            devices.extend(self._scan_macos())
        
        return devices
    
    def _scan_windows(self):
        try:
            import wmi
            c = wmi.WMI()
            devices = []
            for item in c.Win32_PnPEntity():
                if any(vendor in str(item.Description) for vendor in self.supported_vendors.values()):
                    devices.append({
                        'name': item.Description,
                        'device_id': item.DeviceID,
                        'status': item.Status
                    })
            return devices
        except:
            return self._scan_usb_devices()
    
    def _scan_usb_devices(self):
        devices = []
        for dev in usb.core.find(find_all=True):
            vendor_name = self.supported_vendors.get(dev.idVendor, "Unknown")
            devices.append({
                'vendor_id': hex(dev.idVendor),
                'product_id': hex(dev.idProduct),
                'vendor': vendor_name,
                'product': "Unknown"
            })
        return devices
