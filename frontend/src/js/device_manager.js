// frontend/src/js/device-manager.js
class DeviceManager {
    constructor() {
        this.autoDetectionInterval = null;
        this.isAutoDetection = false;
    }

    init() {
        console.log('Device Manager initialized');
        // Initial device scan
        this.scanDevices();
    }

    async scanDevices() {
        try {
            const response = await fetch('/api/devices/scan');
            const devices = await response.json();
            
            App.handleDeviceScan(devices);
            
            return devices;
        } catch (error) {
            console.error('Device scan failed:', error);
            App.showNotification('Device scan failed: ' + error.message, 'danger');
            return [];
        }
    }

    startAutoDetection() {
        if (this.isAutoDetection) {
            this.stopAutoDetection();
            return;
        }

        this.isAutoDetection = true;
        App.showNotification('Auto device detection enabled', 'success');
        
        // Start periodic scanning
        this.autoDetectionInterval = setInterval(() => {
            this.scanDevices();
        }, 3000); // Scan every 3 seconds

        // Update UI
        const button = document.querySelector('button[onclick="deviceManager.startAutoDetection()"]');
        if (button) {
            button.innerHTML = '<i class="fas fa-ban"></i> Disable Auto-Detect';
            button.classList.remove('btn-success');
            button.classList.add('btn-danger');
        }
    }

    stopAutoDetection() {
        this.isAutoDetection = false;
        if (this.autoDetectionInterval) {
            clearInterval(this.autoDetectionInterval);
            this.autoDetectionInterval = null;
        }

        App.showNotification('Auto device detection disabled', 'warning');
        
        // Update UI
        const button = document.querySelector('button[onclick="deviceManager.startAutoDetection()"]');
        if (button) {
            button.innerHTML = '<i class="fas fa-bolt"></i> Enable Auto-Detect';
            button.classList.remove('btn-danger');
            button.classList.add('btn-success');
        }
    }

    getCurrentDevice() {
        return App.currentDevice;
    }

    async installDrivers(deviceInfo) {
        try {
            const response = await fetch('/api/drivers/install', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ device_info: deviceInfo })
            });

            const result = await response.json();
            
            if (result.success) {
                App.showNotification('Drivers installed successfully', 'success');
            } else {
                App.showNotification('Driver installation failed', 'danger');
            }
            
            return result;
        } catch (error) {
            console.error('Driver installation failed:', error);
            App.showNotification('Driver installation failed: ' + error.message, 'danger');
            return { success: false, error: error.message };
        }
    }
}

// Initialize device manager
const deviceManager = new DeviceManager();
