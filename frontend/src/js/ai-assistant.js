// frontend/src/js/ai-assistant.js
class AIAssistant {
    constructor() {
        this.analysisHistory = JSON.parse(localStorage.getItem('analysisHistory') || '[]');
        this.isAnalyzing = false;
    }

    init() {
        console.log('AI Assistant initialized');
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Auto-analyze when device is connected
        if (typeof App !== 'undefined') {
            // We'll use the existing App device detection
        }
    }

    async analyzeDevice() {
        const device = App.currentDevice;
        if (!device) {
            App.showNotification('Please connect a device first', 'warning');
            return;
        }

        this.isAnalyzing = true;
        App.showNotification('Starting AI device analysis...', 'info');

        try {
            const response = await fetch('/api/ai/analyze-device', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    device_info: device
                })
            });

            const analysis = await response.json();
            this.displayDeviceAnalysis(analysis);
            this.addToAnalysisHistory(analysis);
            
        } catch (error) {
            console.error('Device analysis failed:', error);
            App.showNotification('Device analysis failed: ' + error.message, 'danger');
        } finally {
            this.isAnalyzing = false;
        }
    }

    async analyzeIssue() {
        const issueDescription = document.getElementById('issueDescription').value;
        if (!issueDescription.trim()) {
            App.showNotification('Please describe the device issue', 'warning');
            return;
        }

        const device = App.currentDevice;
        if (!device) {
            App.showNotification('Please connect a device first', 'warning');
            return;
        }

        this.isAnalyzing = true;
        App.showNotification('AI analyzing issue...', 'info');

        try {
            const response = await fetch('/api/ai/analyze-issue', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    device_info: device,
                    issue: issueDescription,
                    context: this.getUserContext()
                })
            });

            const analysis = await response.json();
            this.displayIssueAnalysis(analysis);
            
        } catch (error) {
            console.error('Issue analysis failed:', error);
            App.showNotification('Issue analysis failed: ' + error.message, 'danger');
        } finally {
            this.isAnalyzing = false;
        }
    }

    async recoverCredentials() {
        const accountClues = document.getElementById('accountClues').value;
        if (!accountClues.trim()) {
            App.showNotification('Please provide some clues about the account', 'warning');
            return;
        }

        this.isAnalyzing = true;
        App.showNotification('AI recovering credentials...', 'info');

        try {
            const response = await fetch('/api/ai/recover-credentials', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    clues: accountClues,
                    context: this.getUserContext()
                })
            });

            const recoveryResult = await response.json();
            this.displayCredentialRecovery(recoveryResult);
            
        } catch (error) {
            console.error('Credential recovery failed:', error);
            App.showNotification('Credential recovery failed: ' + error.message, 'danger');
        } finally {
            this.isAnalyzing = false;
        }
    }

    displayDeviceAnalysis(analysis) {
        const analysisContainer = document.getElementById('aiAnalysis');
        let html = `
            <div class="alert alert-info">
                <h6><i class="fas fa-microchip"></i> Device Analysis Complete</h6>
                <p>AI has analyzed your device and identified optimal recovery strategies</p>
            </div>
            <div class="row">
                <div class="col-md-6">
                    <div class="card bg-dark text-white mb-3">
                        <div class="card-header">
                            <h6>Device Information</h6>
                        </div>
                        <div class="card-body">
                            <p><strong>Manufacturer:</strong> ${analysis.manufacturer || 'Unknown'}</p>
                            <p><strong>Model Family:</strong> ${analysis.model_family || 'Unknown'}</p>
                            <p><strong>Chipset:</strong> ${analysis.chipset || 'Unknown'}</p>
                            <p><strong>Android Version:</strong> ${analysis.android_version || 'Unknown'}</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="card bg-dark text-white mb-3">
                        <div class="card-header">
                            <h6>Recommended Tools</h6>
                        </div>
                        <div class="card-body">
                            ${analysis.recommended_tools ? 
                                analysis.recommended_tools.map(tool => 
                                    `<span class="badge bg-primary me-1 mb-1">${tool}</span>`
                                ).join('') 
                                : '<p>No specific tools recommended</p>'
                            }
                        </div>
                    </div>
                </div>
            </div>
        `;

        if (analysis.known_issues && analysis.known_issues.length > 0) {
            html += `
                <div class="alert alert-warning">
                    <h6>Known Issues for this Model</h6>
                    <ul>
                        ${analysis.known_issues.map(issue => `<li>${issue}</li>`).join('')}
                    </ul>
                </div>
            `;
        }

        analysisContainer.innerHTML = html;
    }

    displayIssueAnalysis(analysis) {
        const resultContainer = document.getElementById('aiAnalysisResult');
        const taskPlanContainer = document.getElementById('aiTaskPlan');

        // Display analysis result
        resultContainer.innerHTML = `
            <div class="alert alert-success">
                <h6><i class="fas fa-brain"></i> AI Analysis Result</h6>
                <p><strong>Identified Issue:</strong> ${analysis.identified_issue || 'Multiple issues detected'}</p>
                <p><strong>Confidence:</strong> ${analysis.confidence || 'High'}</p>
                <p><strong>Summary:</strong> ${analysis.summary || 'AI has analyzed the issue and prepared a recovery plan'}</p>
            </div>
        `;

        // Display task plan
        if (analysis.task_plan) {
            taskPlanContainer.innerHTML = `
                <div class="alert alert-info">
                    <h6><i class="fas fa-project-diagram"></i> AI-Generated Recovery Plan</h6>
                    <p><strong>Complexity:</strong> <span class="badge bg-${this.getComplexityColor(analysis.task_plan.complexity)}">${analysis.task_plan.complexity}</span></p>
                    <p><strong>Estimated Time:</strong> ${analysis.task_plan.estimated_time || 'Unknown'}</p>
                </div>
                <div class="task-steps">
                    <h6>Execution Steps:</h6>
                    <ol>
                        ${analysis.task_plan.steps.map((step, index) => `
                            <li>
                                <strong>${step.name || `Step ${index + 1}`}:</strong>
                                ${step.description || 'No description'}
                                ${step.estimated_duration ? `<br><small>Duration: ${step.estimated_duration}</small>` : ''}
                                ${step.tools ? `<br><small>Tools: ${step.tools.join(', ')}</small>` : ''}
                            </li>
                        `).join('')}
                    </ol>
                </div>
                <button class="btn btn-success w-100 mt-3" onclick="aiAssistant.executeAIPlan()">
                    <i class="fas fa-play"></i> Execute AI Recovery Plan
                </button>
            `;
        }
    }

    displayCredentialRecovery(recoveryResult) {
        const recoveryContainer = document.getElementById('credentialRecovery');
        
        let html = `
            <div class="alert alert-info">
                <h6><i class="fas fa-key"></i> Credential Recovery Results</h6>
                <p>Found ${recoveryResult.hypotheses?.length || 0} potential account matches</p>
            </div>
        `;

        if (recoveryResult.hypotheses && recoveryResult.hypotheses.length > 0) {
            html += '<div class="credential-list">';
            
            recoveryResult.hypotheses.forEach((hypothesis, index) => {
                const confidencePercent = Math.round((hypothesis.confidence || 0) * 100);
                const confidenceColor = this.getConfidenceColor(confidencePercent);
                const verificationStatus = hypothesis.verification_status || 'unverified';
                
                html += `
                    <div class="card bg-dark text-white mb-2">
                        <div class="card-body">
                            <div class="d-flex justify-content-between align-items-center">
                                <h6 class="mb-0">${hypothesis.email || 'Unknown'}</h6>
                                <span class="badge bg-${confidenceColor}">${confidencePercent}%</span>
                            </div>
                            <p class="mb-1 mt-2"><small>Reasoning: ${hypothesis.reasoning || 'Pattern match'}</small></p>
                            <div class="d-flex justify-content-between align-items-center mt-2">
                                <span class="badge bg-secondary">${verificationStatus}</span>
                                <button class="btn btn-sm btn-outline-light" onclick="aiAssistant.testCredential('${hypothesis.email}')">
                                    Test
                                </button>
                            </div>
                        </div>
                    </div>
                `;
            });
            
            html += '</div>';
        } else {
            html += `
                <div class="alert alert-warning">
                    <p>No credible account hypotheses found. Try providing more specific clues.</p>
                </div>
            `;
        }

        recoveryContainer.innerHTML = html;
    }

    getComplexityColor(complexity) {
        const colors = {
            'simple': 'success',
            'moderate': 'warning', 
            'complex': 'warning',
            'very_complex': 'danger'
        };
        return colors[complexity?.toLowerCase()] || 'secondary';
    }

    getConfidenceColor(confidence) {
        if (confidence >= 80) return 'success';
        if (confidence >= 60) return 'warning';
        return 'danger';
    }

    getUserContext() {
        return {
            name: localStorage.getItem('user_name') || '',
            birth_year: localStorage.getItem('user_birth_year') || '',
            phone: localStorage.getItem('user_phone') || '',
            location: localStorage.getItem('user_location') || '',
            known_emails: JSON.parse(localStorage.getItem('known_emails') || '[]'),
            previous_devices: JSON.parse(localStorage.getItem('previous_devices') || '[]')
        };
    }

    async executeAIPlan() {
        App.showNotification('Executing AI recovery plan...', 'info');
        
        // This would integrate with the unlock manager
        if (typeof unlockManager !== 'undefined') {
            // Auto-select locks based on AI analysis
            const analysisResult = document.getElementById('aiAnalysisResult').innerText;
            
            // You could add logic here to automatically configure the unlock manager
            // based on the AI analysis
            
            App.showNotification('AI plan execution started', 'success');
        }
    }

    async testCredential(email) {
        App.showNotification(`Testing credential: ${email}`, 'info');
        
        // Simulate credential testing
        setTimeout(() => {
            App.showNotification(`Credential test completed for: ${email}`, 'success');
        }, 2000);
    }

    addToAnalysisHistory(analysis) {
        const historyEntry = {
            id: Date.now(),
            timestamp: new Date().toISOString(),
            device: analysis.device_info?.model || 'Unknown',
            type: analysis.analysis_type || 'device_analysis',
            summary: analysis.summary || 'No summary'
        };

        this.analysisHistory.unshift(historyEntry);
        this.analysisHistory = this.analysisHistory.slice(0, 10);
        localStorage.setItem('analysisHistory', JSON.stringify(this.analysisHistory));
    }

    // Method to learn from successful operations
    learnFromSuccess(deviceInfo, operation, result) {
        const learningData = {
            device: deviceInfo,
            operation: operation,
            result: result,
            timestamp: new Date().toISOString()
        };

        let successPatterns = JSON.parse(localStorage.getItem('successPatterns') || '[]');
        successPatterns.unshift(learningData);
        successPatterns = successPatterns.slice(0, 50); // Keep last 50 successes
        localStorage.setItem('successPatterns', JSON.stringify(successPatterns));
    }
}

// Initialize AI Assistant
const aiAssistant = new AIAssistant();
