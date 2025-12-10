// Main JavaScript for Smart Resume Matcher
class ResumeMatcherUI {
    constructor() {
        this.resumeFile = null;
        this.jobDescriptionFile = null;
        this.manualJobText = '';
        this.currentResult = null;

        this.initializeEventListeners();
        this.setupDragAndDrop();
    }

    initializeEventListeners() {
        // File input change for resume
        const resumeFileInput = document.getElementById('resumeFile');
        if (resumeFileInput) {
            resumeFileInput.addEventListener('change', (e) => {
                this.resumeFile = e.target.files[0];
                this.updateFileInfo('resumeUpload', this.resumeFile);
            });
        }

        // File input change for job description
        const jobFileInput = document.getElementById('jobFile');
        if (jobFileInput) {
            jobFileInput.addEventListener('change', (e) => {
                this.jobDescriptionFile = e.target.files[0];
                this.updateFileInfo('jobUpload', this.jobDescriptionFile);
                // Clear textarea when file is selected
                const jobTextArea = document.getElementById('jobText');
                if (jobTextArea) {
                    jobTextArea.value = '';
                    this.manualJobText = '';
                }
            });
        }

        // Textarea for job description
        const jobTextArea = document.getElementById('jobText');
        if (jobTextArea) {
            // Stop click propagation to prevent file upload
            jobTextArea.addEventListener('click', (e) => {
                e.stopPropagation();
            });
            
            jobTextArea.addEventListener('mousedown', (e) => {
                e.stopPropagation();
            });
            
            jobTextArea.addEventListener('input', (e) => {
                this.manualJobText = e.target.value;
                
                // When user types in textarea, clear file selection
                if (e.target.value.trim() && this.jobDescriptionFile) {
                    this.jobDescriptionFile = null;
                    const jobFileInput = document.getElementById('jobFile');
                    if (jobFileInput) {
                        jobFileInput.value = '';
                        this.updateFileInfo('jobUpload', null);
                    }
                }
            });
        }

        // Form submission
        const uploadForm = document.getElementById('uploadForm');
        if (uploadForm) {
            uploadForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                await this.handleSubmit();
            });
        }

        // Reset button
        const resetBtn = document.getElementById('resetBtn');
        if (resetBtn) {
            resetBtn.addEventListener('click', () => {
                this.resetForm();
            });
        }
    }

    setupDragAndDrop() {
        // --- Resume Upload ---
        const resumeUpload = document.getElementById('resumeUpload');
        const resumeFileInput = document.getElementById('resumeFile');

        if (resumeUpload && resumeFileInput) {
            resumeUpload.addEventListener('dragover', (e) => {
                e.preventDefault();
                resumeUpload.classList.add('dragover');
            });

            resumeUpload.addEventListener('dragleave', () => {
                resumeUpload.classList.remove('dragover');
            });

            resumeUpload.addEventListener('drop', (e) => {
                e.preventDefault();
                resumeUpload.classList.remove('dragover');
                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    this.resumeFile = files[0];
                    const dataTransfer = new DataTransfer();
                    dataTransfer.items.add(files[0]);
                    resumeFileInput.files = dataTransfer.files;
                    this.updateFileInfo('resumeUpload', this.resumeFile);
                }
            });

            resumeUpload.addEventListener('click', (e) => {
                if (!e.target.closest('.file-info') && !e.target.closest('textarea')) {
                    resumeFileInput.click();
                }
            });
        }

        // --- Job Description Upload ---
        const jobUpload = document.getElementById('jobUpload');
        const jobFileInput = document.getElementById('jobFile');

        if (jobUpload && jobFileInput) {
            jobUpload.addEventListener('dragover', (e) => {
                if (e.target.id === 'jobText' || e.target.closest('#jobText')) {
                    return;
                }
                e.preventDefault();
                jobUpload.classList.add('dragover');
            });

            jobUpload.addEventListener('dragleave', () => {
                jobUpload.classList.remove('dragover');
            });

            jobUpload.addEventListener('drop', (e) => {
                if (e.target.id === 'jobText' || e.target.closest('#jobText')) {
                    return;
                }
                e.preventDefault();
                jobUpload.classList.remove('dragover');
                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    this.jobDescriptionFile = files[0];
                    const dataTransfer = new DataTransfer();
                    dataTransfer.items.add(files[0]);
                    jobFileInput.files = dataTransfer.files;
                    this.updateFileInfo('jobUpload', this.jobDescriptionFile);
                    
                    // Clear textarea when file is dropped
                    const jobTextArea = document.getElementById('jobText');
                    if (jobTextArea) {
                        jobTextArea.value = '';
                        this.manualJobText = '';
                    }
                }
            });

            jobUpload.addEventListener('click', (e) => {
                // Don't trigger if clicking on textarea, label, or file info
                if (e.target.id === 'jobText' || 
                    e.target.tagName === 'TEXTAREA' || 
                    e.target.htmlFor === 'jobText' ||
                    e.target.closest('#jobText') ||
                    e.target.closest('.file-info') ||
                    e.target.closest('label')) {
                    return;
                }
                jobFileInput.click();
            });
        }
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    updateFileInfo(uploadAreaId, file) {
        const element = document.getElementById(uploadAreaId);
        if (!element) return;
        
        const fileName = element.querySelector('.file-name');
        const fileSize = element.querySelector('.file-size');
        const fileInfo = element.querySelector('.file-info');
        
        if (file) {
            if (fileName) fileName.textContent = file.name;
            if (fileSize) fileSize.textContent = this.formatFileSize(file.size);
            if (fileInfo) fileInfo.style.display = 'block';
        } else {
            if (fileName) fileName.textContent = 'No file selected';
            if (fileSize) fileSize.textContent = '';
            if (fileInfo) fileInfo.style.display = 'none';
        }
    }

    resetForm() {
        const form = document.getElementById('uploadForm');
        if (form) form.reset();
        
        this.resumeFile = null;
        this.jobDescriptionFile = null;
        this.manualJobText = '';
        
        ['resumeUpload', 'jobUpload'].forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                const fileInfo = element.querySelector('.file-info');
                if (fileInfo) fileInfo.style.display = 'none';
            }
        });
        
        const jobTextArea = document.getElementById('jobText');
        if (jobTextArea) jobTextArea.value = '';
        
        this.hideResult();
        this.showAlert('Form has been reset', 'info');
    }

    hideResult() {
        const resultSection = document.getElementById('resultsSection');
        if (resultSection) {
            resultSection.style.display = 'none';
        }
    }

    showResult() {
        const resultSection = document.getElementById('resultsSection');
        if (resultSection) {
            resultSection.style.display = 'block';
            resultSection.style.opacity = '1';
            resultSection.style.transform = 'translateY(0)';
            resultSection.scrollIntoView({ behavior: 'smooth' });
        }
    }

    showLoading(show) {
        const spinner = document.getElementById('loadingSpinner');
        const submitBtn = document.getElementById('analyzeBtn');
        
        if (spinner) spinner.style.display = show ? 'block' : 'none';
        if (submitBtn) {
            submitBtn.disabled = show;
            submitBtn.innerHTML = show ? 
                '<i class="fas fa-spinner fa-spin me-3"></i>Processing...' :
                '<i class="fas fa-magic me-3"></i>Analyze Match with AI';
        }
    }

    showError(message) {
        this.showAlert(message, 'danger');
    }

    showAlert(message, type = 'info') {
        const existingAlert = document.querySelector('.alert');
        if (existingAlert) {
            existingAlert.remove();
        }
        
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-' + type + ' alert-dismissible fade show fixed-top m-3';
        alertDiv.innerHTML = message + '<button type="button" class="btn-close" data-bs-dismiss="alert"></button>';
        
        document.body.appendChild(alertDiv);
        
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }

    async handleSubmit() {
        this.showLoading(true);
        this.hideResult();
        
        try {
            if (!this.resumeFile) {
                this.showError('Please upload a resume file');
                this.showLoading(false);
                return;
            }
            
            let jobDescription = '';
            let jobDescriptionSource = '';
            
            if (this.jobDescriptionFile) {
                jobDescription = await this.readFileAsText(this.jobDescriptionFile);
                jobDescriptionSource = 'file';
            } else if (this.manualJobText && this.manualJobText.trim()) {
                jobDescription = this.manualJobText.trim();
                jobDescriptionSource = 'text';
            } else {
                this.showError('Please provide a job description (upload file or enter text)');
                this.showLoading(false);
                return;
            }
            
            const formData = new FormData();
            formData.append('resume', this.resumeFile);
            
            if (this.jobDescriptionFile) {
                formData.append('job_description', this.jobDescriptionFile);
            }
            
            if (jobDescriptionSource === 'text') {
                formData.append('job_text', jobDescription);
            }
            
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Upload failed');
            }
            
            this.displayResult(data);
            
        } catch (error) {
            console.error('Upload error:', error);
            this.showError(error.message || 'Failed to process files. Please try again.');
        } finally {
            this.showLoading(false);
        }
    }

    readFileAsText(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (e) => resolve(e.target.result);
            reader.onerror = (e) => reject(new Error('Failed to read file'));
            reader.readAsText(file);
        });
    }

    displayResult(result) {
        console.log('Displaying result:', result);
        
        this.showResult();
        
        // Overall score
        const overallScore = result.match_result?.overall_score || 0;
        const overallScoreElement = document.getElementById('overallScore');
        if (overallScoreElement) {
            overallScoreElement.textContent = overallScore.toFixed(1) + '%';
            
            if (overallScore >= 85) {
                overallScoreElement.className = 'display-1 fw-bold mb-4 text-success';
            } else if (overallScore >= 70) {
                overallScoreElement.className = 'display-1 fw-bold mb-4 text-warning';
            } else {
                overallScoreElement.className = 'display-1 fw-bold mb-4 text-danger';
            }
        }
        
        // Progress bar
        const scoreProgressElement = document.getElementById('scoreProgress');
        if (scoreProgressElement) {
            scoreProgressElement.style.width = overallScore + '%';
            
            if (overallScore >= 85) {
                scoreProgressElement.className = 'progress-bar bg-success';
            } else if (overallScore >= 70) {
                scoreProgressElement.className = 'progress-bar bg-warning';
            } else {
                scoreProgressElement.className = 'progress-bar bg-danger';
            }
        }
        
        // Component scores
        const skillScoreElement = document.getElementById('skillScore');
        if (skillScoreElement && result.match_result?.skill_score !== undefined) {
            skillScoreElement.textContent = result.match_result.skill_score.toFixed(1) + '%';
        }
        
        const expScoreElement = document.getElementById('expScore');
        if (expScoreElement && result.match_result?.experience_score !== undefined) {
            expScoreElement.textContent = result.match_result.experience_score.toFixed(1) + '%';
        }
        
        const eduScoreElement = document.getElementById('eduScore');
        if (eduScoreElement && result.match_result?.education_score !== undefined) {
            eduScoreElement.textContent = result.match_result.education_score.toFixed(1) + '%';
        }
        
        const semScoreElement = document.getElementById('semScore');
        if (semScoreElement && result.match_result?.semantic_score !== undefined) {
            semScoreElement.textContent = result.match_result.semantic_score.toFixed(1) + '%';
        }
        
        // AI Explanation
        const aiExplanationElement = document.getElementById('aiExplanation');
        if (aiExplanationElement) {
            if (result.ai_explanation) {
                aiExplanationElement.innerHTML = result.ai_explanation.replace(/\n/g, '<br>');
            } else {
                aiExplanationElement.textContent = 'No explanation available.';
            }
        }
        
        // Recommendation
        const recommendationTextElement = document.getElementById('recommendationText');
        if (recommendationTextElement && result.recommendation) {
            recommendationTextElement.textContent = result.recommendation.text || '';
        }
        
        // Skills
        if (result.match_result?.skill_details) {
            const skillDetails = result.match_result.skill_details;
            
            const matchedSkillsElement = document.getElementById('matchedSkills');
            if (matchedSkillsElement) {
                matchedSkillsElement.innerHTML = this.formatSkillTags(skillDetails.required_matches, 'success');
            }
            
            const missingSkillsElement = document.getElementById('missingSkills');
            if (missingSkillsElement) {
                missingSkillsElement.innerHTML = this.formatSkillTags(skillDetails.missing_required, 'warning');
            }
            
            const preferredSkillsElement = document.getElementById('preferredSkills');
            if (preferredSkillsElement) {
                preferredSkillsElement.innerHTML = this.formatSkillTags(skillDetails.preferred_matches, 'primary');
            }
        }
        
        // Resume Summary
        const resumeSummaryElement = document.getElementById('resumeSummary');
        if (resumeSummaryElement && result.resume_info) {
            resumeSummaryElement.innerHTML = 
                '<p><strong>File:</strong> ' + result.resume_info.filename + '</p>' +
                '<p><strong>Skills found:</strong> ' + result.resume_info.skills_count + '</p>' +
                '<p><strong>Experience:</strong> ' + result.resume_info.experience_years + ' years</p>' +
                '<p><strong>Education:</strong> ' + (result.resume_info.education?.join(', ') || 'Not detected') + '</p>';
        }
        
        // Job Summary
        const jobSummaryElement = document.getElementById('jobSummary');
        if (jobSummaryElement && result.job_info) {
            jobSummaryElement.innerHTML = 
                '<p><strong>Source:</strong> ' + (result.job_info.source || 'Unknown') + '</p>' +
                '<p><strong>Required skills:</strong> ' + (result.job_info.required_skills?.join(', ') || 'None specified') + '</p>' +
                '<p><strong>Preferred skills:</strong> ' + (result.job_info.preferred_skills?.join(', ') || 'None specified') + '</p>' +
                '<p><strong>Experience required:</strong> ' + result.job_info.experience_required + ' years</p>';
        }
    }

    formatSkillTags(skills, type = 'primary') {
        if (!skills || skills.length === 0) {
            return '<p class="text-muted"><em>None found</em></p>';
        }
        
        let colorClass = '';
        switch(type) {
            case 'success': colorClass = 'bg-success text-white'; break;
            case 'warning': colorClass = 'bg-warning text-dark'; break;
            case 'primary': colorClass = 'bg-primary text-white'; break;
            default: colorClass = 'bg-secondary text-white';
        }
        
        return skills.map(skill => 
            '<span class="badge ' + colorClass + ' me-1 mb-1 p-2">' + skill + '</span>'
        ).join(' ');
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new ResumeMatcherUI();
    console.log('Smart Resume Matcher UI initialized');
});