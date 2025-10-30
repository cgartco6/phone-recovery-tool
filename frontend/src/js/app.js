// frontend/src/js/app.js
class PhoneRecoveryApp {
    constructor() {
        this.connectedDevices = [];
        this.activeTasks = new Map();
        this.init();
    }

    init() {
        document.getElementById('scanDevices').addEventListener('click', () => this.scanDevices());
        document.getElementById('analyzeIssue').addEventListener('click', () => this.analyzeIssue());
    }

    async scanDevices() {
        try {
            const response = await fetch('/api/devices/scan', {
                method: 'POST'
            });
            const devices = await response.json();
            this.displayDevices(devices);
        } catch (error) {
            console.error('Device scan failed:', error);
        }
    }

    displayDevices(devices) {
        const deviceList = document.getElementById('deviceList');
        deviceList.innerHTML = '';

        devices.forEach(device => {
            const deviceCard = this.createDeviceCard(device);
            deviceList.appendChild(deviceCard);
        });
    }

    createDeviceCard(device) {
        const card = document.createElement('div');
        card.className = 'card device-card mb-2';
        card.innerHTML = `
            <div class="card-body">
                <h6>${device.vendor} ${device.product || 'Device'}</h6>
                <p class="mb-1">Vendor ID: ${device.vendor_id}</p>
                <p class="mb-1">Product ID: ${device.product_id}</p>
                <button class="btn btn-sm btn-outline-primary create-task-btn" 
                        data-device-id="${device.vendor_id}-${device.product_id}">
                    Create Recovery Task
                </button>
            </div>
        `;

        card.querySelector('.create-task-btn').addEventListener('click', () => {
            this.showTaskCreationModal(device);
        });

        return card;
    }

    async analyzeIssue() {
        const issueDescription = document.getElementById('issueDescription').value;
        if (!issueDescription.trim()) return;

        const analysisDiv = document.getElementById('aiAnalysis');
        analysisDiv.innerHTML = '<div class="spinner-border" role="status"></div>';

        try {
            const response = await fetch('/api/ai/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    issue: issueDescription,
                    device: this.connectedDevices[0] // Assuming one device for simplicity
                })
            });

            const analysis = await response.json();
            this.displayAIAnalysis(analysis);
        } catch (error) {
            console.error('AI analysis failed:', error);
        }
    }

    displayAIAnalysis(analysis) {
        const analysisDiv = document.getElementById('aiAnalysis');
        analysisDiv.innerHTML = `
            <div class="alert alert-info">
                <h6>AI Analysis Result:</h6>
                <p>${analysis.summary}</p>
                <h6>Recommended Steps:</h6>
                <ol>
                    ${analysis.steps.map(step => `<li>${step}</li>`).join('')}
                </ol>
                <button class="btn btn-primary" onclick="app.createRecoveryTask()">
                    Create Recovery Task
                </button>
            </div>
        `;
    }
}

// Initialize application
const app = new PhoneRecoveryApp();
