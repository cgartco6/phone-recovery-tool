// frontend/src/js/photo-recovery.js
class PhotoRecoveryManager {
    constructor() {
        this.isRecovering = false;
        this.recoveryHistory = JSON.parse(localStorage.getItem('recoveryHistory') || '[]');
    }

    async startComprehensiveRecovery() {
        if (this.isRecovering) {
            alert('Recovery already in progress');
            return;
        }

        const device = deviceManager.getCurrentDevice();
        if (!device) {
            alert('Please select a device first');
            return;
        }

        this.isRecovering = true;
        
        // Get recovery options
        const options = {
            intensity: document.getElementById('recoveryIntensity').value,
            recoverPhotos: document.getElementById('recoverPhotos').checked,
            recoverVideos: document.getElementById('recoverVideos').checked,
            recoverDocuments: document.getElementById('recoverDocuments').checked
        };

        this.updateRecoveryStatus('Starting recovery process...', 0);

        try {
            const response = await fetch('/api/recovery/start-comprehensive', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    device_info: device,
                    options: options
                })
            });

            const result = await response.json();
            
            if (result.success) {
                // Start progress tracking
                this.trackRecoveryProgress(result.recovery_id);
                
                // Store in history
                this.addToRecoveryHistory(result);
            } else {
                this.updateRecoveryStatus('Recovery failed to start', 0);
                this.isRecovering = false;
            }
        } catch (error) {
            console.error('Recovery start failed:', error);
            this.updateRecoveryStatus('Recovery failed: ' + error.message, 0);
            this.isRecovering = false;
        }
    }

    async trackRecoveryProgress(recoveryId) {
        const progressInterval = setInterval(async () => {
            try {
                const response = await fetch(`/api/recovery/progress/${recoveryId}`);
                const progress = await response.json();
                
                this.updateRecoveryStatus(progress.status, progress.percentage);
                
                if (progress.completed) {
                    clearInterval(progressInterval);
                    this.isRecovering = false;
                    this.displayRecoveryResults(progress.results);
                }
            } catch (error) {
                console.error('Progress tracking failed:', error);
                clearInterval(progressInterval);
                this.isRecovering = false;
            }
        }, 2000);
    }

    updateRecoveryStatus(status, percentage) {
        const statusElement = document.getElementById('recoveryStatus');
        const progressBar = document.querySelector('.progress-bar');
        const statsElement = document.getElementById('recoveryStats');

        if (statusElement) statusElement.textContent = status;
        if (progressBar) {
            progressBar.style.width = `${percentage}%`;
            progressBar.textContent = `${percentage}%`;
        }

        if (percentage === 100) {
            statsElement.innerHTML = `
                <div class="alert alert-success">
                    <i class="fas fa-check-circle"></i> Recovery Completed Successfully!
                </div>
            `;
        }
    }

    displayRecoveryResults(results) {
        const statsElement = document.getElementById('recoveryStats');
        
        statsElement.innerHTML = `
            <div class="row text-center">
                <div class="col-4">
                    <h3 class="text-success">${results.photos_recovered}</h3>
                    <small>Photos</small>
                </div>
                <div class="col-4">
                    <h3 class="text-info">${results.videos_recovered}</h3>
                    <small>Videos</small>
                </div>
                <div class="col-4">
                    <h3 class="text-warning">${results.documents_recovered}</h3>
                    <small>Documents</small>
                </div>
            </div>
            <div class="mt-3">
                <p><i class="fas fa-hdd"></i> Total Size: ${this.formatFileSize(results.recovered_size)}</p>
                <p><i class="fas fa-folder-open"></i> Location: ${results.recovery_path}</p>
            </div>
        `;

        // Update global stats
        const currentPhotos = parseInt(localStorage.getItem('photosRecovered') || '0');
        localStorage.setItem('photosRecovered', currentPhotos + results.photos_recovered);
        app.updateStats();
    }

    addToRecoveryHistory(recoveryResult) {
        const historyEntry = {
            id: Date.now(),
            timestamp: new Date().toISOString(),
            device: recoveryResult.device_info?.model || 'Unknown',
            results: recoveryResult
        };

        this.recoveryHistory.unshift(historyEntry);
        this.recoveryHistory = this.recoveryHistory.slice(0, 10); // Keep last 10 entries
        localStorage.setItem('recoveryHistory', JSON.stringify(this.recoveryHistory));
        
        this.displayRecoveryHistory();
    }

    displayRecoveryHistory() {
        const historyElement = document.getElementById('recoveryHistory');
        
        if (this.recoveryHistory.length === 0) {
            historyElement.innerHTML = '<p class="text-muted">No recovery history available</p>';
            return;
        }

        let html = '<div class="list-group">';
        
        this.recoveryHistory.forEach(entry => {
            const date = new Date(entry.timestamp).toLocaleString();
            html += `
                <div class="list-group-item bg-dark text-white">
                    <div class="d-flex w-100 justify-content-between">
                        <h6 class="mb-1">${entry.device}</h6>
                        <small>${date}</small>
                    </div>
                    <p class="mb-1">
                        Photos: ${entry.results.photos_recovered} | 
                        Videos: ${entry.results.videos_recovered} | 
                        Size: ${this.formatFileSize(entry.results.recovered_size)}
                    </p>
                </div>
            `;
        });
        
        html += '</div>';
        historyElement.innerHTML = html;
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
}

// Initialize photo recovery manager
const photoRecovery = new PhotoRecoveryManager();
