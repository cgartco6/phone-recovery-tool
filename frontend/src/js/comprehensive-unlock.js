// frontend/src/js/comprehensive-unlock.js
class ComprehensiveUnlockManager {
    constructor() {
        this.selectedLocks = new Set();
        this.currentDevice = null;
        this.init();
    }

    init() {
        // Initialize checkboxes
        document.querySelectorAll('.form-check-input').forEach(checkbox => {
            checkbox.addEventListener('change', (e) => {
                if (e.target.checked) {
                    this.selectedLocks.add(e.target.id.replace('Check', ''));
                } else {
                    this.selectedLocks.delete(e.target.id.replace('Check', ''));
                }
            });
        });

        document.getElementById('startComprehensiveUnlock').addEventListener('click', () => this.startUnlock());
        document.getElementById('installAllDrivers').addEventListener('click', () => this.installAllDrivers());
        document.getElementById('downloadTools').addEventListener('click', () => this.downloadTools());
    }

    async startUnlock() {
        if (this.selectedLocks.size === 0) {
            alert('Please select at least one lock type to remove');
            return;
        }

        if (!this.currentDevice) {
            alert('Please scan for devices first');
            return;
        }

        const issues = Array.from(this.selectedLocks);
        
        try {
            const response = await fetch('/api/unlock/comprehensive', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    device_info: this.currentDevice,
                    issues: issues
                })
            });

            const result = await response.json();
            this.displayUnlockResults(result);
        } catch (error) {
            console.error('Comprehensive unlock failed:', error);
        }
    }

    async installAllDrivers() {
        if (!this.currentDevice) {
            alert('Please scan for devices first');
            return;
        }

        const statusDiv = document.getElementById('driverSoftwareStatus');
        statusDiv.innerHTML = '<div class="spinner-border" role="status"></div> Installing drivers...';

        try {
            const response = await fetch('/api/drivers/install-all', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    device_info: this.currentDevice
                })
            });

            const result = await response.json();
            this.displayDriverResults(result);
        } catch (error) {
            console.error('Driver installation failed:', error);
        }
    }

    displayUnlockResults(results) {
        const resultsDiv = document.createElement('div');
        resultsDiv.className = 'mt-3';

        let html = '<h6>Comprehensive Unlock Results:</h6>';
        
        for (const [issue, result] of Object.entries(results)) {
            if (issue === 'overall_success') continue;
            
            const success = result.success ? 'success' : 'danger';
            const icon = result.success ? 'check-circle' : 'times-circle';
            
            html += `
                <div class="alert alert-${success}">
                    <i class="fas fa-${icon}"></i> 
                    <strong>${issue.toUpperCase()}:</strong> 
                    ${result.success ? 'SUCCESS' : 'FAILED'}
                    ${result.method ? ` (Method: ${result.method})` : ''}
                    ${result.error ? `<br><small>Error: ${result.error}</small>` : ''}
                </div>
            `;
        }

        html += `<div class="alert alert-${results.overall_success ? 'success' : 'danger'}">
                    <strong>Overall Result:</strong> ${results.overall_success ? 'COMPLETE SUCCESS' : 'PARTIAL FAILURE'}
                 </div>`;

        resultsDiv.innerHTML = html;
        document.getElementById('driverSoftwareStatus').appendChild(resultsDiv);
    }
}

// Initialize comprehensive unlock manager
const unlockManager = new ComprehensiveUnlockManager();
