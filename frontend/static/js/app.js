// Application State
const state = {
    files: [],
    currentFile: null,
    sessionId: null,
    detectedType: null,
    detectedFormat: null,
    availableTargets: [],
    theme: localStorage.getItem('theme') || 'light',
    downloadAttempts: 0,
    downloadBlocked: false
};

// Format recommendations based on common use cases
const FORMAT_RECOMMENDATIONS = {
    'image': {
        'png': 'pdf',
        'jpg': 'pdf',
        'jpeg': 'pdf',
        'bmp': 'png',
        'tiff': 'pdf',
        'gif': 'png',
        'webp': 'png',
        'ico': 'png'
    },
    'document': {
        'pdf': 'docx',
        'docx': 'pdf',
        'doc': 'pdf',
        'xlsx': 'pdf',
        'xls': 'pdf'
    }
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
    
    // Cleanup on page unload/close
    window.addEventListener('beforeunload', cleanupOnUnload);
    
    // Cleanup on visibility change (tab close/switch)
    document.addEventListener('visibilitychange', handleVisibilityChange);
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
        
        // Show format compatibility notification
        if (processedFiles.length > 1) {
            if (commonTargets.length === 0) {
                showNotification('⚠️ 所選檔案格式不一致，無法批量轉換，請分批處理', 5000);
            } else if (commonTargets.length < processedFiles[0].availableTargets.length) {
                showNotification(`📋 已選 ${processedFiles.length} 個檔案，可共同轉換為: ${commonTargets.join(', ').toUpperCase()}`, 4000);
            } else {
                showNotification(`✓ 已選 ${processedFiles.length} 個檔案，可批量轉換`, 3000);
            }
        }
        
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
    
    // Get recommended format
    const recommendedFormat = getRecommendedFormat();
    
    state.availableTargets.forEach(format => {
        const option = document.createElement('option');
        option.value = format;
        option.textContent = format.toUpperCase() + (format === recommendedFormat ? ' (推薦)' : '');
        elements.targetFormat.appendChild(option);
    });
    
    // Auto-select recommended format
    if (recommendedFormat && state.availableTargets.includes(recommendedFormat)) {
        elements.targetFormat.value = recommendedFormat;
        elements.convertBtn.disabled = false;
        
        // Show notification about auto-selection
        showNotification(`已自動選擇推薦格式: ${recommendedFormat.toUpperCase()}`, 2000);
    }
}

function getRecommendedFormat() {
    /**
     * Get the recommended target format based on detected file type and format
     */
    if (!state.files.length) return null;
    
    // For single file
    if (state.files.length === 1) {
        const file = state.files[0];
        if (FORMAT_RECOMMENDATIONS[file.type] && FORMAT_RECOMMENDATIONS[file.type][file.format]) {
            return FORMAT_RECOMMENDATIONS[file.type][file.format];
        }
    }
    
    // For multiple files - find common recommendation
    const recommendations = state.files.map(file => {
        if (FORMAT_RECOMMENDATIONS[file.type] && FORMAT_RECOMMENDATIONS[file.type][file.format]) {
            return FORMAT_RECOMMENDATIONS[file.type][file.format];
        }
        return null;
    }).filter(Boolean);
    
    // If all files have same recommendation, use it
    if (recommendations.length === state.files.length && 
        recommendations.every(r => r === recommendations[0])) {
        return recommendations[0];
    }
    
    // Otherwise, return first available common format
    return state.availableTargets[0] || null;
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
            
            // More detailed progress message
            const progressMsg = totalFiles > 1 
                ? `正在轉換第 ${i + 1} / ${totalFiles} 個檔案...` 
                : '正在轉換...';
            updateProgress(percent, progressMsg);
            
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
                    originalName: file.name,
                    sessionId: file.sessionId  // Add sessionId to results
                });
            } catch (error) {
                results.push({
                    success: false,
                    filename: file.name,
                    error: error.message,
                    errorDetails: analyzeError(error.message, file)
                });
            }
        }
        
        updateProgress(100, '轉換完成');
        
        // Show results first
        showResults(results);
        
        // Auto download based on file count
        const successCount = results.filter(r => r.success).length;
        
        if (successCount === 1) {
            // Single file: auto download immediately
            setTimeout(() => {
                autoDownloadFiles(results);
            }, 500);
        } else if (successCount > 1) {
            // Multiple files: show batch download option prominently
            showNotification(`✓ ${successCount} 個檔案轉換完成，請使用「打包下載全部」`, 4000);
        }
        
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
    
    // Track download attempts
    state.downloadAttempts = successfulResults.length;
    state.downloadBlocked = false;
    
    // Download each file with a small delay to avoid browser blocking
    successfulResults.forEach((result, index) => {
        setTimeout(() => {
            const link = document.createElement('a');
            link.href = result.downloadUrl;
            link.download = result.filename;
            link.style.display = 'none';
            document.body.appendChild(link);
            
            try {
                link.click();
                console.log(`Auto-downloading: ${result.filename}`);
            } catch (e) {
                console.error('Download failed:', e);
                state.downloadBlocked = true;
            }
            
            document.body.removeChild(link);
            
            // Check if downloads might be blocked after first attempt
            if (index === 0 && successfulResults.length > 1) {
                setTimeout(() => {
                    checkDownloadStatus(successfulResults);
                }, 1000);
            }
        }, index * 300); // 300ms delay between downloads
    });
    
    // Show notification
    if (successfulResults.length === 1) {
        showNotification(`正在自動下載: ${successfulResults[0].filename}`, 3000);
    } else {
        showNotification(`正在自動下載 ${successfulResults.length} 個檔案...`, 3000);
    }
}

function checkDownloadStatus(results) {
    /**
     * Check if browser might be blocking downloads and show notification
     */
    if (!state.downloadBlocked && results.length > 1) {
        showNotification(
            `💡 提示：若瀏覽器阻擋下載，請在結果頁面手動下載檔案`,
            5000
        );
    }
}

async function downloadBatch(results) {
    /**
     * Download all successful results as a ZIP file
     */
    try {
        console.log('[BATCH DOWNLOAD] Starting batch download...');
        console.log('[BATCH DOWNLOAD] Results:', results);
        
        // Show loading state
        showNotification('正在打包檔案...', 2000);
        
        // Prepare files info for batch download - use sessionId from results
        const filesInfo = results
            .filter(r => r.sessionId && r.filename)
            .map(result => ({
                session_id: result.sessionId,
                filename: result.filename
            }));
        
        console.log('[BATCH DOWNLOAD] Files info:', filesInfo);
        
        if (filesInfo.length === 0) {
            console.error('[BATCH DOWNLOAD] No files to download!');
            showNotification('⚠️ 沒有可下載的檔案', 3000);
            return;
        }
        
        const requestBody = {
            files: filesInfo
        };
        
        console.log('[BATCH DOWNLOAD] Request body:', JSON.stringify(requestBody, null, 2));
        console.log('[BATCH DOWNLOAD] Making fetch request...');
        
        // Request batch download
        const response = await fetch('/api/download-batch', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestBody)
        });
        
        console.log('[BATCH DOWNLOAD] Response status:', response.status);
        console.log('[BATCH DOWNLOAD] Response headers:', [...response.headers.entries()]);
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
            console.error('[BATCH DOWNLOAD] Error response:', errorData);
            throw new Error(errorData.error || `Server error: ${response.status}`);
        }
        
        // Get the ZIP file blob
        console.log('[BATCH DOWNLOAD] Reading response as blob...');
        const blob = await response.blob();
        console.log('[BATCH DOWNLOAD] Blob size:', blob.size, 'bytes');
        
        if (blob.size === 0) {
            throw new Error('Downloaded file is empty');
        }
        
        const url = window.URL.createObjectURL(blob);
        console.log('[BATCH DOWNLOAD] Created blob URL:', url);
        
        // Create download link
        const link = document.createElement('a');
        link.href = url;
        link.download = `converted_files_${Date.now()}.zip`;
        link.style.display = 'none';
        document.body.appendChild(link);
        link.click();
        console.log('[BATCH DOWNLOAD] Download link clicked');
        document.body.removeChild(link);
        
        // Clean up
        setTimeout(() => {
            window.URL.revokeObjectURL(url);
            console.log('[BATCH DOWNLOAD] Cleaned up blob URL');
        }, 100);
        
        showNotification(`✓ 已開始下載 ${filesInfo.length} 個檔案（ZIP 壓縮包）`, 3000);
        console.log('[BATCH DOWNLOAD] Success!');
        
    } catch (error) {
        console.error('[BATCH DOWNLOAD] FAILED:', error);
        console.error('[BATCH DOWNLOAD] Error stack:', error.stack);
        showNotification(`❌ 批量下載失敗: ${error.message}，請嘗試單獨下載`, 5000);
    }
}

function analyzeError(errorMessage, file) {
    /**
     * Analyze error and provide actionable suggestions
     */
    const error = errorMessage.toLowerCase();
    
    // Common error patterns and solutions
    if (error.includes('unsupported') || error.includes('not supported')) {
        return {
            reason: '不支援的格式轉換',
            solution: `${file.format.toUpperCase()} 無法直接轉換為此格式，請嘗試其他目標格式`
        };
    }
    
    if (error.includes('file not found') || error.includes('not found')) {
        return {
            reason: '檔案遺失',
            solution: '請重新上傳檔案後再試'
        };
    }
    
    if (error.includes('encrypted') || error.includes('password')) {
        return {
            reason: 'PDF 檔案已加密',
            solution: '請先移除密碼保護後再上傳'
        };
    }
    
    if (error.includes('corrupted') || error.includes('invalid')) {
        return {
            reason: '檔案損壞或格式錯誤',
            solution: '請確認檔案完整性，或嘗試使用其他工具重新儲存'
        };
    }
    
    if (error.includes('size') || error.includes('large')) {
        return {
            reason: '檔案過大',
            solution: '請壓縮檔案或分割後再上傳（限制 50MB）'
        };
    }
    
    if (error.includes('timeout')) {
        return {
            reason: '轉換逾時',
            solution: '檔案處理時間過長，請減少檔案大小或頁數後重試'
        };
    }
    
    // Default error
    return {
        reason: '轉換失敗',
        solution: '請檢查檔案格式是否正確，或嘗試其他轉換格式'
    };
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
    
    // Determine notification style based on message content
    let bgColor = '#4CAF50'; // Default success green
    if (message.includes('⚠️') || message.includes('阻擋')) {
        bgColor = '#ff9800'; // Warning orange
    } else if (message.includes('❌') || message.includes('失敗')) {
        bgColor = '#f44336'; // Error red
    } else if (message.includes('💡') || message.includes('提示')) {
        bgColor = '#2196F3'; // Info blue
    }
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = 'notification fade-in';
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${bgColor};
        color: white;
        padding: 15px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        z-index: 10000;
        font-size: 14px;
        max-width: 350px;
        font-weight: 500;
        line-height: 1.5;
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
    
    // Count successful conversions
    const successfulResults = results.filter(r => r.success);
    const hasMultipleSuccess = successfulResults.length > 1;
    
    // Add batch download button for multiple successful files
    if (hasMultipleSuccess) {
        const batchDownloadBtn = document.createElement('button');
        batchDownloadBtn.className = 'btn btn-primary btn-large batch-download-btn';
        batchDownloadBtn.id = 'batchDownloadBtn';
        batchDownloadBtn.innerHTML = `
            <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                <polyline points="7 10 12 15 17 10"></polyline>
                <line x1="12" y1="15" x2="12" y2="3"></line>
            </svg>
            打包下載全部 (${successfulResults.length} 個檔案)
        `;
        batchDownloadBtn.onclick = () => downloadBatch(successfulResults);
        
        elements.resultsList.appendChild(batchDownloadBtn);
        
        // Add separator
        const separator = document.createElement('div');
        separator.className = 'results-separator';
        separator.textContent = '個別下載：';
        elements.resultsList.appendChild(separator);
        
        // Add floating "Back to Top" button when there are many files
        if (successfulResults.length > 3) {
            showBackToTopButton();
        }
    }
    
    results.forEach(result => {
        const resultItem = createResultItem(result);
        elements.resultsList.appendChild(resultItem);
    });
    
    // Scroll to top to show download button
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function showBackToTopButton() {
    // Remove existing button if any
    const existing = document.querySelector('.back-to-top-btn');
    if (existing) {
        existing.remove();
    }
    
    // Create back to top button
    const backToTopBtn = document.createElement('button');
    backToTopBtn.className = 'back-to-top-btn';
    backToTopBtn.innerHTML = `
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="18 15 12 9 6 15"></polyline>
        </svg>
        <span class="btn-text">返回頂部</span>
    `;
    backToTopBtn.onclick = scrollToTop;
    
    document.body.appendChild(backToTopBtn);
    
    // Show/hide button based on scroll position
    window.addEventListener('scroll', () => {
        if (window.scrollY > 300) {
            backToTopBtn.classList.add('visible');
        } else {
            backToTopBtn.classList.remove('visible');
        }
    });
}

function scrollToTop() {
    window.scrollTo({ top: 0, behavior: 'smooth' });
    
    // Highlight the download button briefly
    setTimeout(() => {
        const downloadBtn = document.getElementById('batchDownloadBtn');
        if (downloadBtn) {
            downloadBtn.classList.add('highlight-pulse');
            setTimeout(() => {
                downloadBtn.classList.remove('highlight-pulse');
            }, 2000);
        }
    }, 500);
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
                <div class="result-status success">轉換成功</div>
            </div>
            <a href="${result.downloadUrl}" class="btn btn-primary" download>下載</a>
        `;
    } else {
        const errorDetailsHTML = result.errorDetails 
            ? `<div class="error-details">
                <div class="error-reason">❌ ${result.errorDetails.reason}</div>
                <div class="error-solution">💡 ${result.errorDetails.solution}</div>
               </div>`
            : '';
        
        div.innerHTML = `
            <div class="result-icon error">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <line x1="18" y1="6" x2="6" y2="18"></line>
                    <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
            </div>
            <div class="result-info">
                <div class="result-filename">${result.filename}</div>
                <div class="result-status error">轉換失敗</div>
                ${errorDetailsHTML}
            </div>
        `;
    }
    
    return div;
}

// Reset
async function resetApp() {
    // Remove back-to-top button if it exists
    const backToTopBtn = document.querySelector('.back-to-top-btn');
    if (backToTopBtn) {
        backToTopBtn.remove();
    }
    
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

// Cleanup handlers
function cleanupOnUnload(event) {
    // Use sendBeacon for reliable cleanup on page unload
    if (state.files.length > 0) {
        for (const file of state.files) {
            if (file.sessionId) {
                // sendBeacon is more reliable than fetch for beforeunload
                navigator.sendBeacon(`/api/cleanup/${file.sessionId}`);
            }
        }
    }
}

let visibilityTimer = null;

function handleVisibilityChange() {
    if (document.hidden) {
        // User switched away or minimized - set a timer
        // If they don't come back within 5 minutes, cleanup
        visibilityTimer = setTimeout(() => {
            if (state.files.length > 0) {
                for (const file of state.files) {
                    if (file.sessionId) {
                        fetch(`/api/cleanup/${file.sessionId}`, {
                            method: 'DELETE',
                            keepalive: true
                        }).catch(err => console.error('Cleanup failed:', err));
                    }
                }
            }
        }, 5 * 60 * 1000); // 5 minutes
    } else {
        // User came back - cancel the cleanup timer
        if (visibilityTimer) {
            clearTimeout(visibilityTimer);
            visibilityTimer = null;
        }
    }
}

// Initialize app
init();
