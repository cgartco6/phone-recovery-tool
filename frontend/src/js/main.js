// frontend/src/js/main.js
class UniversalRecoveryApp {
    constructor() {
        this.currentView = 'dashboard';
        this.connectedDevices = [];
        this.init();
    }

    init() {
        // Initialize all components
        this.initializeNavigation();
        this.loadAgentStatus();
        this.updateStats();
        
        // Auto-scan for devices on startup
        setTimeout(() => {
            deviceManager.scanDevices();
        }, 1000);
    }

    initializeNavigation() {
        // Handle navigation clicks
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const target = e.target.getAttribute('href').substring(1);
                this.showView(target);
            });
        });
    }

    showView(viewName) {
        // Hide all views
        document.querySelectorAll('.container.mt-4, .container.mt-5').forEach(container => {
            container.style.display = 'none';
        });

        // Show selected view
        const targetElement = document.getElementById(viewName);
        if (targetElement) {
            targetElement.style.display = 'block';
        }

        // Update active nav link
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });
        document.querySelector(`[href="#${viewName}"]`).classList.add('active');

        this.currentView = viewName;
    }

    async loadAgentStatus() {
        try {
            const response = await fetch('/api/ai/agent-status');
            const agents = await response.json();
            this.displayAgentStatus(agents);
        } catch (error) {
            console.error('Failed to load agent status:', error);
        }
    }

    displayAgentStatus(agents) {
        const statusContainer = document.getElementById('agentStatus');
        let html = '';

        for (const [agentId, agent] of Object.entries(agents)) {
            const statusClass = agent.status === 'online' ? 'status-online' : 'status-offline';
            
            html += `
                <div class="col-md-6 col-lg-4 mb-3">
                    <div class="agent-status ${statusClass}">
                        <div class="d-flex justify-content-between align-items-center">
                            <div>
                                <h6 class="mb-1">${agent.name}</h6>
                                <small class="text-muted">${agent.current_task || 'Idle'}</small>
                            </div>
                            <span class="badge ${agent.status === 'online' ? 'bg-success' : 'bg-danger'}">
                                ${agent.status}
                            </span>
                        </div>
                        <div class="mt-2">
                            ${agent.capabilities.map(cap => 
                                `<span class="badge bg-secondary me-1">${cap}</span>`
                            ).join('')}
                        </div>
                    </div>
                </div>
            `;
        }

        statusContainer.innerHTML = html;
    }

    updateStats() {
        // Update statistics from local storage or API
        const stats = {
            connectedDevices: this.connectedDevices.length,
            successfulUnlocks: localStorage.getItem('successfulUnlocks') || 0,
            photosRecovered: localStorage.getItem('photosRecovered') || 0,
            aiAgents: 12
        };

        document.getElementById('connectedDevices').textContent = stats.connectedDevices;
        document.getElementById('successfulUnlocks').textContent = stats.successfulUnlocks;
        document.getElementById('photosRecovered').textContent = stats.photosRecovered;
        document.getElementById('aiAgents').textContent = stats.aiAgents;
    }
}

// Initialize main application
const app = new UniversalRecoveryApp();
