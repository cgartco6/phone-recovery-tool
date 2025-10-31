// frontend/src/js/unlock-manager.js
class UnlockManager {
    constructor() {
        this.currentUnlockOperation = null;
        this.unlockHistory = JSON.parse(localStorage.getItem('unlockHistory') || '[]');
        this.isUnlocking = false;
    }

    init() {
        console.log('Unlock Manager initialized');
        this.displayUnlockHistory();
    }

    async startComprehensiveUnlock() {
        if (this.isUnlocking) {
            App.showNotification('Unlock operation already in progress', 'warning');
            return;
        }

        const device = App.currentDevice;
        if (!device) {
            App.showNotification('Please connect a device first', 'warning');
            return;
        }

        // Get selected lock types
        const selectedLocks = this.getSelectedLocks();
        if (selectedLocks.length === 0) {
            App.showNotification('Please select at least one lock type to remove', 'warning');
            return;
        }

        this.isUnlocking = true;
        this.currentUnlockOperation = {
            id: Date.now(),
            device: device,
            locks: selectedLocks,
            startTime: new Date().toISOString(),
            status: 'starting'
        };

        App.showNotification(`Starting comprehensive unlock for ${selectedLocks.length} lock types`, 'info');

        try {
            const response = await fetch('/api/unlock/comprehensive', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    device_info: device,
                    issues: selectedLocks
                })
            });

            const result = await response.json();
            this.handleUnlockResult(result);
            
        } catch (error) {
            console.error('Unlock operation failed:', error);
            App.showNotification('Unlock operation failed: ' + error.message, 'danger');
            this.isUnlocking = false;
        }
    }

    getSelectedLocks() {
        const locks = [];
        const lockTypes = [
            { id: 'frpCheck', type: 'frp' },
            { id: 'kgCheck', type: 'kg_lock' },
            { id: 'mdmCheck', type: 'mdm' },
            { id: 'googleAccountCheck', type: 'google_account' },
            { id: 'payjoyCheck', type: 'payjoy' },
            { id: 'payatCheck', type: 'pay@' }
        ];

        lockTypes.forEach(lock => {
            const checkbox = document.getElementById(lock.id);
            if (checkbox && checkbox.checked) {
                locks.push(lock.type);
            }
        });

        return locks;
    }

    handleUnlockResult(result) {
        this.currentUnlockOperation.endTime = new Date().toISOString();
        this.currentUnlockOperation.result = result;
        this.currentUnlockOperation.status = result.overall_success ? 'completed' : 'failed';

        // Update UI
        this.displayUnlockProgress(result);
        this.addToUnlockHistory(this.currentUnlockOperation);

        // Update stats
        if (result.overall_success) {
            const currentUnlocks = parseInt(localStorage.getItem('successfulUnlocks') || '0');
            localStorage.setItem('successfulUnlocks', currentUnlocks + 1);
            App.updateStats();
        }

        this.isUnlocking = false;
        App.showNotification(
            `Unlock operation ${result.overall_success ? 'completed successfully' : 'failed'}`,
            result.overall_success ? 'success' : 'danger'
        );
    }

    displayUnlockProgress(result) {
        const progressContainer = document.getElementById('unlockProgress');
        let html = '<div class="unlock-progress">';

        // Overall result
        html += `
            <div class="alert alert-${result.overall_success ? 'success' : 'danger'}">
                <h6>Overall Result: ${result.overall_success ? 'SUCCESS' : 'FAILED'}</h6>
                ${result.failed_on ? `<small>Failed on: ${result.failed_on}</small>` : ''}
            </div>
        `;

        // Individual lock results
        for (const [lockType, lockResult] of Object.entries(result)) {
            if (lockType === 'overall_success' || lockType === 'failed_on' || lockType === 'device_analysis') continue;

            const success = lockResult.success;
            const icon = success ? 'check-circle' : 'times-circle';
            const alertClass = success ? 'success' : 'danger';

            html += `
                <div class="alert alert-${alertClass}">
                    <i class="fas fa-${icon}"></i>
                    <strong>${lockType.toUpperCase()}:</strong>
                    ${success ? 'REMOVED' : 'FAILED'}
                    ${lockResult.method ? ` (${lockResult.method})` : ''}
                    ${lockResult.error ? `<br><small>Error: ${lockResult.error}</small>` : ''}
                </div>
            `;
        }

        // Device analysis
        if (result.device_analysis) {
            html += `
                <div class="alert alert-info">
                    <h6>Device Analysis:</h6>
                    <small>
                        Manufacturer: ${result.device_analysis.manufacturer}<br>
                        Model Family: ${result.device_analysis.model_family}<br>
                        Chipset: ${result.device_analysis.chipset}<br>
                        Recommended Tools: ${result.device_analysis.recommended_tools?.join(', ')}
                    </small>
                </div>
            `;
        }

        html += '</div>';
        progressContainer.innerHTML = html;
    }

    addToUnlockHistory(operation) {
        this.unlockHistory.unshift(operation);
        // Keep only last 20 operations
        this.unlockHistory = this.unlockHistory.slice(0, 20);
        localStorage.setItem('unlockHistory', JSON.stringify(this.unlockHistory));
    }

    displayUnlockHistory() {
        // This would be called when the unlock section is shown
        const historyContainer = document.getElementById('unlockHistory');
        if (!historyContainer) return;

        if (this.unlockHistory.length === 0) {
            historyContainer.innerHTML = '<p class="text-muted">No unlock history available</p>';
            return;
        }

        let html = '<div class="list-group">';
        this.unlockHistory.forEach(operation => {
            const date = new Date(operation.startTime).toLocaleString();
            const successCount = operation.result ? 
                Object.values(operation.result).filter(r => r.success).length : 0;
            const totalLocks = operation.locks.length;

            html += `
                <div class="list-group-item bg-dark text-white">
                    <div class="d-flex w-100 justify-content-between">
                        <h6 class="mb-1">${operation.device?.model || 'Unknown Device'}</h6>
                        <small>${date}</small>
                    </div>
                    <p class="mb-1">
                        Locks: ${operation.locks.join(', ')}<br>
                        Success: ${successCount}/${totalLocks}
                    </p>
                    <small>Status: ${operation.status}</small>
                </div>
            `;
        });
        html += '</div>';
        historyContainer.innerHTML = html;
    }

    async removeSingleLock(lockType, deviceInfo) {
        try {
            const response = await fetch('/api/unlock/single', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    device_info: deviceInfo,
                    lock_type: lockType
                })
            });

            const result = await response.json();
            return result;
        } catch (error) {
            console.error(`Failed to remove ${lockType}:`, error);
            return { success: false, error: error.message };
        }
    }

    // Method to check if device is unlockable
    async checkDeviceUnlockability(deviceInfo) {
        try {
            const response = await fetch('/api/unlock/check', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ device_info: deviceInfo })
            });

            const result = await response.json();
            return result;
        } catch (error) {
            console.error('Device unlockability check failed:', error);
            return { unlockable: false, error: error.message };
        }
    }
}

// Initialize unlock manager
const unlockManager = new UnlockManager();
