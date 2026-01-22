// Application State
const state = {
    files: [],
    currentFile: null,
    sessionId: null,
    detectedType: null,
    detectedFormat: null,
    availableTargets: [],
    theme: localStorage.getItem('theme') || 'light'
};

// DOM Elements
const elements = {
    uploadArea: document.getElementById('uploadArea'),
    fileInput: document.getElementById('fileInput'),
    selectFileBtn: document.getElementById('selectFileBtn'),
    filesSection: document.getElementById('filesSection'),
    filesList: document.getElementById('filesList'),
    clearBtn: document.getElementById('clearBtn'),
    conversionSection: document.getElementById('conversionSection'),
    targetFormat: document.getElementById('targetFormat'),
    convertBtn: document.getElementById('convertBtn'),
    progressSection: document.getElementById('progressSection'),
    progressFill: document.getElementById('progressFill'),
    progressText: document.getElementById('progressText'),
    progressPercent: document.getElementById('progressPercent'),
    resultsSection: document.getElementById('resultsSection'),
    resultsList: document.getElementById('resultsList'),
    newConversionBtn: document.getElementById('newConversionBtn'),
    themeToggle: document.getElementById('themeToggle')
};

// Initialize
function init() {
    setupEventListeners();
    applyTheme();
}

// Event Listeners
function setupEventListeners() {
    // File selection
    elements.selectFileBtn.addEventListener('click', () => elements.fileInput.click());
    elements.fileInput.addEventListener('change', handleFileSelect);
    
    // Drag and drop
    elements.uploadArea.addEventListener('dragover', handleDragOver);
    elements.uploadArea.addEventListener('dragleave', handleDragLeave);
    elements.uploadArea.addEventListener('drop', handleDrop);
    
    // Clear files
    elements.clearBtn.addEventListener('click', clearFiles);
    
    // Target format change
    elements.targetFormat.addEventListener('change', handleFormatChange);
    
    // Convert
    elements.convertBtn.addEventListener('click', convertFiles);
    
    // New conversion
    elements.newConversionBtn.addEventListener('click', resetApp);
    
    // Theme toggle
    elements.themeToggle.addEventListener('click', toggleTheme);
}

// Theme Management
function applyTheme() {
    document.documentElement.setAttribute('data-theme', state.theme);
}

function toggleTheme() {
    state.theme = state.theme === 'light' ? 'dark' : 'light';
    localStorage.setItem('theme', state.theme);
    applyTheme();
}

// File Handling
function handleFileSelect(e) {
    const files = Array.from(e.target.files);
    processFiles(files);
}

function handleDragOver(e) {
    e.preventDefault();
    elements.uploadArea.classList.add('dragover');
}

function handleDragLeave(e) {
    e.preventDefault();
    elements.uploadArea.classList.remove('dragover');
}

function handleDrop(e) {
    e.preventDefault();
    elements.uploadArea.classList.remove('dragover');
    const files = Array.from(e.dataTransfer.files);
    processFiles(files);
}

async function processFiles(files) {
    if (files.length === 0) return;
    
    try {
        showLoading();
        
        // Process all files
        const processedFiles = [];
        let commonType = null;
        let commonTargets = [];
        
        for (const file of files) {
            // Upload and detect format
            const formData = new FormData();
            formData.append('file', file);
            
            const response = await fetch('/api/detect', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (!data.success) {
                throw new Error(data.error);
            }
            
            processedFiles.push({
                name: data.filename,
                size: file.size,
                type: data.detected_type,
                format: data.detected_format,
                sessionId: data.session_id,
                availableTargets: data.available_targets
            });
            
            // Track common type and targets
            if (!commonType) {
                commonType = data.detected_type;
                commonTargets = data.available_targets;
            } else {
                // Find intersection of available targets
                commonTargets = commonTargets.filter(t => 
                    data.available_targets.includes(t)
                );
            }
        }
        
        // Update state
        state.files = processedFiles;
        state.detectedType = commonType;
        state.availableTargets = commonTargets;
        
        // Update UI
        hideLoading();
        showFilesSection();
        showConversionSection();
        
    } catch (error) {
        hideLoading();
        showError('文件上傳失敗: ' + error.message);
    }
}

// UI Updates
function showFilesSection() {
    elements.filesSection.style.display = 'block';
    elements.filesList.innerHTML = '';
    
    state.files.forEach((file, index) => {
        const fileItem = createFileItem(file, index);
        elements.filesList.appendChild(fileItem);
    });
}

function createFileItem(file, index) {
    const div = document.createElement('div');
    div.className = 'file-item fade-in';
    div.innerHTML = `
        <svg class="file-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"></path>
            <polyline points="13 2 13 9 20 9"></polyline>
        </svg>
        <div class="file-info">
            <div class="file-name">${file.name}</div>
            <div class="file-meta">${formatFileSize(file.size)} • ${file.format.toUpperCase()} (${file.type})</div>
        </div>
    `;
    return div;
}

function showConversionSection() {
    elements.conversionSection.style.display = 'block';
    
    // Populate target formats
    elements.targetFormat.innerHTML = '<option value="">請選擇格式</option>';
    state.availableTargets.forEach(format => {
        const option = document.createElement('option');
        option.value = format;
        option.textContent = format.toUpperCase();
        elements.targetFormat.appendChild(option);
    });
}

function handleFormatChange() {
    elements.convertBtn.disabled = !elements.targetFormat.value;
}

function clearFiles() {
    state.files = [];
    state.sessionId = null;
    elements.filesList.innerHTML = '';
    elements.filesSection.style.display = 'none';
    elements.conversionSection.style.display = 'none';
}

// Conversion
async function convertFiles() {
    if (state.files.length === 0 || !elements.targetFormat.value) return;
    
    try {
        // Show progress
        elements.conversionSection.style.display = 'none';
        elements.progressSection.style.display = 'block';
        updateProgress(0, '正在轉換...');
        
        const results = [];
        const totalFiles = state.files.length;
        
        // Convert each file
        for (let i = 0; i < state.files.length; i++) {
            const file = state.files[i];
            const percent = Math.round(((i + 1) / totalFiles) * 100);
            
            updateProgress(percent, `正在轉換 ${i + 1}/${totalFiles}...`);
            
            try {
                const response = await fetch('/api/convert', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        session_id: file.sessionId,
                        filename: file.name,
                        target_format: elements.targetFormat.value
                    })
                });
                
                const data = await response.json();
                
                if (!data.success) {
                    throw new Error(data.error);
                }
                
                results.push({
                    success: true,
                    filename: data.output_filename,
                    downloadUrl: data.download_url,
                    originalName: file.name
                });
            } catch (error) {
                results.push({
                    success: false,
                    filename: file.name,
                    error: error.message
                });
            }
        }
        
        updateProgress(100, '轉換完成');
        
        // Auto download successful files
        setTimeout(() => {
            autoDownloadFiles(results);
            showResults(results);
        }, 500);
        
    } catch (error) {
        showResults([{
            success: false,
            filename: '批量轉換',
            error: error.message
        }]);
    }
}

function updateProgress(percent, text) {
    elements.progressFill.style.width = percent + '%';
    elements.progressPercent.textContent = percent + '%';
    elements.progressText.textContent = text;
}

function autoDownloadFiles(results) {
    /**
     * Automatically download all successfully converted files
     */
    const successfulResults = results.filter(r => r.success);
    
    if (successfulResults.length === 0) {
        return; // No files to download
    }
    
    // Download each file with a small delay to avoid browser blocking
    successfulResults.forEach((result, index) => {
        setTimeout(() => {
            const link = document.createElement('a');
            link.href = result.downloadUrl;
            link.download = result.filename;
            link.style.display = 'none';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            console.log(`Auto-downloading: ${result.filename}`);
        }, index * 300); // 300ms delay between downloads
    });
    
    // Show notification
    if (successfulResults.length === 1) {
        showNotification(`正在自動下載: ${successfulResults[0].filename}`);
    } else {
        showNotification(`正在自動下載 ${successfulResults.length} 個文件...`);
    }
}

function showNotification(message, duration = 3000) {
    /**
     * Show a temporary notification message
     */
    // Remove existing notification if any
    const existing = document.querySelector('.notification');
    if (existing) {
        existing.remove();
    }
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = 'notification fade-in';
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #4CAF50;
        color: white;
        padding: 15px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        z-index: 10000;
        font-size: 14px;
        max-width: 300px;
    `;
    
    document.body.appendChild(notification);
    
    // Auto remove after duration
    setTimeout(() => {
        notification.classList.add('fade-out');
        setTimeout(() => notification.remove(), 300);
    }, duration);
}

function showResults(results) {
    elements.progressSection.style.display = 'none';
    elements.filesSection.style.display = 'none';
    elements.resultsSection.style.display = 'block';
    elements.resultsList.innerHTML = '';
    
    results.forEach(result => {
        const resultItem = createResultItem(result);
        elements.resultsList.appendChild(resultItem);
    });
}

function createResultItem(result) {
    const div = document.createElement('div');
    div.className = 'result-item fade-in';
    
    if (result.success) {
        div.innerHTML = `
            <div class="result-icon success">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="20 6 9 17 4 12"></polyline>
                </svg>
            </div>
            <div class="result-info">
                <div class="result-filename">${result.filename}</div>
                <div class="result-status success">轉換成功 · 已自動下載</div>
            </div>
            <a href="${result.downloadUrl}" class="btn btn-primary" download>重新下載</a>
        `;
    } else {
        div.innerHTML = `
            <div class="result-icon error">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <line x1="18" y1="6" x2="6" y2="18"></line>
                    <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
            </div>
            <div class="result-info">
                <div class="result-filename">${result.filename}</div>
                <div class="result-status error">轉換失敗: ${result.error}</div>
            </div>
        `;
    }
    
    return div;
}

// Reset
async function resetApp() {
    // Cleanup all sessions
    if (state.files.length > 0) {
        try {
            for (const file of state.files) {
                if (file.sessionId) {
                    await fetch(`/api/cleanup/${file.sessionId}`, {
                        method: 'DELETE'
                    });
                }
            }
        } catch (error) {
            console.error('Cleanup failed:', error);
        }
    }
    
    // Reset state
    state.files = [];
    state.sessionId = null;
    state.detectedType = null;
    state.detectedFormat = null;
    state.availableTargets = [];
    
    // Reset UI
    elements.fileInput.value = '';
    elements.filesSection.style.display = 'none';
    elements.conversionSection.style.display = 'none';
    elements.progressSection.style.display = 'none';
    elements.resultsSection.style.display = 'none';
    elements.targetFormat.value = '';
    elements.convertBtn.disabled = true;
}

// Utilities
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

function showLoading() {
    elements.progressSection.style.display = 'block';
    updateProgress(0, '上傳中...');
}

function hideLoading() {
    elements.progressSection.style.display = 'none';
}

function showError(message) {
    alert(message);
}

// Initialize app
init();
