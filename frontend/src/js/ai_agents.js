// frontend/src/js/ai-agents.js
class AICoordinatorFrontend {
    constructor() {
        this.activeAgents = new Map();
        this.workflowState = {};
    }

    async analyzeCredentials() {
        const clues = document.getElementById('accountClues').value;
        if (!clues.trim()) return;

        const analysisDiv = document.getElementById('credentialAnalysis');
        analysisDiv.innerHTML = '<div class="spinner-border" role="status"></div>';

        try {
            const response = await fetch('/api/ai/analyze-credentials', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    clues: clues,
                    context: this.getUserContext()
                })
            });

            const analysis = await response.json();
            this.displayCredentialAnalysis(analysis);
        } catch (error) {
            console.error('Credential analysis failed:', error);
        }
    }

    displayCredentialAnalysis(analysis) {
        const analysisDiv = document.getElementById('credentialAnalysis');
        
        let html = `
            <div class="alert alert-info">
                <h6>AI Analysis Complete</h6>
                <p>Found ${analysis.hypotheses.length} potential email addresses</p>
            </div>
            <div class="mt-3">
                <h6>Top Email Hypotheses:</h6>
        `;

        analysis.hypotheses.forEach(hypothesis => {
            const confidencePercent = Math.round(hypothesis.confidence * 100);
            html += `
                <div class="card mb-2">
                    <div class="card-body">
                        <div class="d-flex justify-content-between">
                            <span class="fw-bold">${hypothesis.email}</span>
                            <span class="badge bg-${this.getConfidenceColor(confidencePercent)}">
                                ${confidencePercent}% Confidence
                            </span>
                        </div>
                        <small class="text-muted">${hypothesis.reasoning}</small>
                        <div class="mt-2">
                            <span class="badge bg-secondary">${hypothesis.verification_status}</span>
                        </div>
                    </div>
                </div>
            `;
        });

        analysisDiv.innerHTML = html;
    }

    async createAITaskPlan(deviceInfo, issue) {
        const planDiv = document.getElementById('aiTaskPlan');
        planDiv.innerHTML = '<div class="spinner-border" role="status"></div>';

        try {
            const response = await fetch('/api/ai/create-task-plan', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    device_info: deviceInfo,
                    issue: issue,
                    context: this.workflowState
                })
            });

            const taskPlan = await response.json();
            this.displayTaskPlan(taskPlan);
        } catch (error) {
            console.error('Task planning failed:', error);
        }
    }

    displayTaskPlan(taskPlan) {
        const planDiv = document.getElementById('aiTaskPlan');
        
        let html = `
            <div class="alert alert-success">
                <h6>AI-Generated Recovery Plan</h6>
                <p>Complexity: <span class="badge bg-warning">${taskPlan.complexity}</span></p>
            </div>
            <div class="mt-3">
                <h6>Execution Steps:</h6>
        `;

        taskPlan.subtasks.forEach((subtask, index) => {
            html += `
                <div class="card mb-2">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-center">
                            <h6 class="mb-0">Step ${index + 1}: ${subtask.description}</h6>
                            <span class="badge bg-info">${subtask.agent_type}</span>
                        </div>
                        <div class="mt-2">
                            <small class="text-muted">
                                <i class="fas fa-clock"></i> ${subtask.estimated_duration}s | 
                                <i class="fas fa-tools"></i> ${subtask.required_tools.join(', ')}
                            </small>
                        </div>
                        ${subtask.dependencies.length > 0 ? `
                            <div class="mt-1">
                                <small>Depends on: ${subtask.dependencies.join(', ')}</small>
                            </div>
                        ` : ''}
                    </div>
                </div>
            `;
        });

        html += `
            <div class="mt-3">
                <button class="btn btn-success" onclick="aiCoordinator.executeTaskPlan()">
                    <i class="fas fa-play"></i> Execute AI Plan
                </button>
            </div>
        `;

        planDiv.innerHTML = html;
    }

    getConfidenceColor(confidence) {
        if (confidence >= 80) return 'success';
        if (confidence >= 60) return 'warning';
        return 'danger';
    }

    getUserContext() {
        // Get user context from form or stored data
        return {
            name: localStorage.getItem('user_name') || '',
            birth_year: localStorage.getItem('user_birth_year') || '',
            phone: localStorage.getItem('user_phone') || '',
            known_emails: JSON.parse(localStorage.getItem('known_emails') || '[]')
        };
    }
}

// Initialize AI Coordinator
const aiCoordinator = new AICoordinatorFrontend();
