// AI Evaluation Tool - Frontend Logic

// Global state
let currentQuery = null;
let currentScoringQuery = null;
let autoSaveTimeout = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
});

function initializeApp() {
    // Load initial status
    loadStatus();

    // Set up event listeners
    setupEventListeners();

    // Auto-refresh every 5 seconds
    setInterval(loadStatus, 5000);
}

function setupEventListeners() {
    // Refresh button
    document.getElementById('refreshBtn').addEventListener('click', loadStatus);

    // Action buttons
    document.getElementById('runBatchBtn').addEventListener('click', runChatGPTBatch);
    document.getElementById('enterGoogleBtn').addEventListener('click', openGoogleModal);
    document.getElementById('scoreBtn').addEventListener('click', openScoringModal);
    document.getElementById('exportBtn').addEventListener('click', exportReport);

    // Google Modal
    const googleModal = document.getElementById('googleModal');
    googleModal.querySelector('.close').addEventListener('click', () => closeModal('googleModal'));
    document.getElementById('copyQueryBtn').addEventListener('click', copyQueryToClipboard);
    document.getElementById('saveGoogleBtn').addEventListener('click', saveGoogleResponse);
    document.getElementById('skipQueryBtn').addEventListener('click', skipGoogleQuery);

    // Auto-save for Google response
    document.getElementById('googleResponse').addEventListener('input', handleGoogleResponseInput);

    // Scoring Modal
    const scoringModal = document.getElementById('scoringModal');
    scoringModal.querySelector('.close').addEventListener('click', () => closeModal('scoringModal'));
    document.getElementById('submitScoresBtn').addEventListener('click', submitScores);
    document.getElementById('skipScoringBtn').addEventListener('click', skipScoring);

    // Range sliders - update value display
    const sliders = document.querySelectorAll('input[type="range"]');
    sliders.forEach(slider => {
        slider.addEventListener('input', (e) => {
            const valueSpan = e.target.nextElementSibling;
            if (valueSpan && valueSpan.classList.contains('score-value')) {
                valueSpan.textContent = e.target.value;
            }
        });
    });

    // Close modals on outside click
    window.addEventListener('click', (e) => {
        if (e.target.classList.contains('modal')) {
            e.target.style.display = 'none';
        }
    });
}

// API Functions

async function loadStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();

        if (data.success) {
            updateUI(data.stats);
        } else {
            showMessage('Error loading status', 'error');
        }
    } catch (error) {
        console.error('Error loading status:', error);
    }
}

function updateUI(stats) {
    // Update stat cards
    document.getElementById('totalQueries').textContent = stats.total_queries;
    document.getElementById('chatgptDone').textContent = stats.chatgpt_responses;
    document.getElementById('googleDone').textContent = stats.google_responses;
    document.getElementById('scoredCount').textContent = stats.scored;
    document.getElementById('completeCount').textContent = stats.fully_complete;

    // Update progress bar
    const progress = stats.percent_complete;
    document.getElementById('progressBar').style.width = `${progress}%`;
    document.getElementById('progressText').textContent = `${Math.round(progress)}% Complete`;

    // Update batch processing status
    if (stats.batch_processing && stats.batch_processing.running) {
        showBatchProgress(stats.batch_processing);
    } else {
        hideBatchProgress();

        // Show completion message if batch just finished
        if (stats.batch_processing && stats.batch_processing.completed && stats.batch_processing.completion_message) {
            showBatchCompletionMessage(stats.batch_processing);
        }
    }

    // Update scoring threshold status
    updateScoringThreshold(stats.chatgpt_responses, stats.google_responses);

    // Update scoring count badge
    updateScoringCount();
}

async function runChatGPTBatch() {
    const batchSize = parseInt(document.getElementById('batchSize').value);
    const btn = document.getElementById('runBatchBtn');

    btn.disabled = true;
    btn.textContent = 'Starting...';

    try {
        const response = await fetch('/api/run-chatgpt-batch', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ batch_size: batchSize })
        });

        const data = await response.json();

        if (data.success) {
            showMessage(data.message, 'success');
            showBatchProgress({ running: true, progress: 0, total: data.count });
        } else {
            showMessage(data.error, 'error');
            btn.disabled = false;
            btn.textContent = `Run ChatGPT Batch (${batchSize} queries)`;
        }
    } catch (error) {
        showMessage('Error starting batch', 'error');
        btn.disabled = false;
        btn.textContent = `Run ChatGPT Batch (${batchSize} queries)`;
    }
}

function showBatchProgress(status) {
    const progressDiv = document.getElementById('batchProgress');
    const progressText = document.getElementById('batchProgressText');
    const btn = document.getElementById('runBatchBtn');

    progressDiv.style.display = 'flex';
    progressText.textContent = `Processing ${status.progress}/${status.total}... ${status.current_query || ''}`;
    btn.disabled = true;
    btn.textContent = 'Processing...';
}

function hideBatchProgress() {
    const progressDiv = document.getElementById('batchProgress');
    const btn = document.getElementById('runBatchBtn');
    const batchSize = document.getElementById('batchSize').value;

    progressDiv.style.display = 'none';
    btn.disabled = false;
    btn.textContent = `Run ChatGPT Batch (${batchSize} queries)`;
}

function showBatchCompletionMessage(batchStatus) {
    // Determine message type based on success/failure
    let messageType = 'success';
    if (batchStatus.error_count > 0) {
        messageType = batchStatus.success_count > 0 ? 'warning' : 'error';
    }

    // Build detailed message
    let message = batchStatus.completion_message;

    // Add error details if any
    if (batchStatus.error_count > 0 && batchStatus.errors && batchStatus.errors.length > 0) {
        message += '\n\nError details:\n';
        batchStatus.errors.forEach((err, idx) => {
            if (err.error) {
                message += `• ${err.error}\n`;
            }
        });

        if (batchStatus.error_count > batchStatus.errors.length) {
            message += `• ... and ${batchStatus.error_count - batchStatus.errors.length} more errors`;
        }
    }

    // Show message with appropriate styling
    showDetailedMessage(message, messageType);

    // Acknowledge the completion
    acknowledgeBatchCompletion();
}

async function acknowledgeBatchCompletion() {
    try {
        await fetch('/api/acknowledge-batch', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
    } catch (error) {
        console.error('Error acknowledging batch:', error);
    }
}

function showDetailedMessage(message, type = 'info') {
    const container = document.getElementById('statusMessages');

    const messageDiv = document.createElement('div');
    messageDiv.className = `status-message ${type} detailed-message`;

    // Preserve line breaks in message
    messageDiv.style.whiteSpace = 'pre-line';
    messageDiv.textContent = message;

    // Add close button for error/warning messages
    if (type === 'error' || type === 'warning') {
        const closeBtn = document.createElement('button');
        closeBtn.textContent = '×';
        closeBtn.className = 'message-close-btn';
        closeBtn.onclick = () => messageDiv.remove();
        messageDiv.appendChild(closeBtn);
    }

    container.appendChild(messageDiv);

    // Auto-remove after 10 seconds (longer for errors)
    const timeout = (type === 'error' || type === 'warning') ? 15000 : 8000;
    setTimeout(() => {
        messageDiv.remove();
    }, timeout);
}

async function openGoogleModal() {
    try {
        const response = await fetch('/api/queries-needing-google?size=1');
        const data = await response.json();

        if (data.success && data.queries.length > 0) {
            currentQuery = data.queries[0];
            displayGoogleQuery(currentQuery);
            openModal('googleModal');
        } else {
            showMessage('No queries need Google AI responses', 'info');
        }
    } catch (error) {
        showMessage('Error loading query', 'error');
    }
}

function displayGoogleQuery(query) {
    document.getElementById('currentQueryId').textContent = query.id;
    document.getElementById('queryMeta').textContent =
        `${query.category} | ${query.quality} | ${query.intent_clarity}`;
    document.getElementById('queryText').textContent = query.query;
    document.getElementById('googleResponse').value = '';
}

function copyQueryToClipboard() {
    const queryText = currentQuery.query;
    navigator.clipboard.writeText(queryText).then(() => {
        showMessage('Query copied to clipboard!', 'success');
    }).catch(() => {
        showMessage('Failed to copy query', 'error');
    });
}

function handleGoogleResponseInput() {
    // Clear existing timeout
    if (autoSaveTimeout) {
        clearTimeout(autoSaveTimeout);
    }

    // Set new timeout for auto-save
    autoSaveTimeout = setTimeout(() => {
        const indicator = document.getElementById('autoSaveIndicator');
        indicator.style.display = 'block';
        setTimeout(() => {
            indicator.style.display = 'none';
        }, 2000);
    }, 2000);
}

async function saveGoogleResponse() {
    const response = document.getElementById('googleResponse').value.trim();

    if (!response) {
        showMessage('Please enter a response', 'warning');
        return;
    }

    try {
        const result = await fetch('/api/save-google-response', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                query_id: currentQuery.id,
                response: response
            })
        });

        const data = await result.json();

        if (data.success) {
            showMessage('Response saved!', 'success');
            closeModal('googleModal');
            loadStatus();

            // Load next query
            setTimeout(openGoogleModal, 500);
        } else {
            showMessage(data.error, 'error');
        }
    } catch (error) {
        showMessage('Error saving response', 'error');
    }
}

function skipGoogleQuery() {
    closeModal('googleModal');
    // Could implement skip logic here if needed
}

function updateScoringThreshold(chatgptCount, googleCount) {
    const THRESHOLD = 50;
    const thresholdProgress = document.getElementById('thresholdProgress');
    const thresholdMessage = document.getElementById('thresholdMessage');
    const scoreBtn = document.getElementById('scoreBtn');

    // Update progress text
    thresholdProgress.textContent = `ChatGPT: ${chatgptCount}/50 | Google AI: ${googleCount}/50`;

    // Check if threshold is met for both platforms
    const thresholdMet = chatgptCount >= THRESHOLD && googleCount >= THRESHOLD;

    if (thresholdMet) {
        // Hide threshold message and enable button
        thresholdMessage.style.display = 'none';
        scoreBtn.disabled = false;
        scoreBtn.textContent = 'Score Responses (Stratified Sample)';
    } else {
        // Show threshold message and keep button disabled
        thresholdMessage.style.display = 'block';
        scoreBtn.disabled = true;

        // Calculate how many more responses needed
        const chatgptNeeded = Math.max(0, THRESHOLD - chatgptCount);
        const googleNeeded = Math.max(0, THRESHOLD - googleCount);

        if (chatgptNeeded > 0 && googleNeeded > 0) {
            scoreBtn.textContent = `Need ${chatgptNeeded} more ChatGPT + ${googleNeeded} more Google responses`;
        } else if (chatgptNeeded > 0) {
            scoreBtn.textContent = `Need ${chatgptNeeded} more ChatGPT responses`;
        } else if (googleNeeded > 0) {
            scoreBtn.textContent = `Need ${googleNeeded} more Google responses`;
        }
    }
}

async function updateScoringCount() {
    try {
        const response = await fetch('/api/queries-needing-scores');
        const data = await response.json();

        if (data.success) {
            const badge = document.getElementById('scoringCount');
            badge.textContent = `${data.total_needing_scores} queries need scoring`;
        }
    } catch (error) {
        console.error('Error updating scoring count:', error);
    }
}

async function openScoringModal() {
    try {
        // First, check if manual sample has been generated
        const sampleStatusResponse = await fetch('/api/manual-sample-status');
        const sampleStatus = await sampleStatusResponse.json();

        // If sample not generated yet, generate it now
        if (sampleStatus.success && !sampleStatus.generated) {
            showMessage('Generating stratified sample for manual scoring...', 'info');

            const generateResponse = await fetch('/api/generate-manual-sample', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            const generateData = await generateResponse.json();

            if (!generateData.success) {
                showMessage(generateData.error || 'Failed to generate sample', 'error');
                return;
            }

            showMessage(`Sample generated: ${generateData.sample_size} diverse queries selected for manual scoring`, 'success');
        }

        // Now load the queries for scoring (will be filtered by sample)
        const response = await fetch('/api/queries-needing-scores');
        const data = await response.json();

        if (data.success && data.queries.length > 0) {
            currentScoringQuery = data.queries[0];
            displayScoringQuery(currentScoringQuery);
            openModal('scoringModal');
        } else {
            showMessage('No queries need scoring', 'info');
        }
    } catch (error) {
        showMessage('Error loading query', 'error');
    }
}

function displayScoringQuery(query) {
    // Query info
    document.getElementById('scoreQueryId').textContent = query.id;
    document.getElementById('scoreQueryMeta').textContent =
        `${query.category} | ${query.quality} | ${query.intent_clarity}`;
    document.getElementById('scoreQueryText').textContent = query.query;

    // Responses
    document.getElementById('chatgptResponse').textContent =
        query.chatgpt_response?.response || 'No response';
    document.getElementById('googleResponseDisplay').textContent =
        query.google_response?.response || 'No response';

    // Reset form
    resetScoringForm();
}

function resetScoringForm() {
    // Reset sliders to 3
    const sliders = document.querySelectorAll('.scoring-form input[type="range"]');
    sliders.forEach(slider => {
        slider.value = 3;
        const valueSpan = slider.nextElementSibling;
        if (valueSpan) valueSpan.textContent = 3;
    });

    // Uncheck checkboxes
    document.getElementById('chatgptIntent').checked = false;
    document.getElementById('googleIntent').checked = false;
    document.getElementById('chatgptFollowups').checked = false;
    document.getElementById('googleFollowups').checked = false;

    // Clear notes
    document.getElementById('scoreNotes').value = '';
}

async function submitScores() {
    const scores = {
        chatgpt_relevance: parseInt(document.getElementById('chatgptRelevance').value),
        chatgpt_completeness: parseInt(document.getElementById('chatgptCompleteness').value),
        chatgpt_source_quality: parseInt(document.getElementById('chatgptSourceQuality').value),
        chatgpt_intent_understood: document.getElementById('chatgptIntent').checked,
        chatgpt_followups_needed: document.getElementById('chatgptFollowups').checked,

        google_relevance: parseInt(document.getElementById('googleRelevance').value),
        google_completeness: parseInt(document.getElementById('googleCompleteness').value),
        google_source_quality: parseInt(document.getElementById('googleSourceQuality').value),
        google_intent_understood: document.getElementById('googleIntent').checked,
        google_followups_needed: document.getElementById('googleFollowups').checked,

        notes: document.getElementById('scoreNotes').value
    };

    try {
        const response = await fetch('/api/save-scores', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                query_id: currentScoringQuery.id,
                scores: scores
            })
        });

        const data = await response.json();

        if (data.success) {
            showMessage('Scores saved!', 'success');
            closeModal('scoringModal');
            loadStatus();

            // Load next query
            setTimeout(openScoringModal, 500);
        } else {
            showMessage(data.error, 'error');
        }
    } catch (error) {
        showMessage('Error saving scores', 'error');
    }
}

function skipScoring() {
    closeModal('scoringModal');
    // Could implement skip logic here if needed
}

async function exportReport() {
    const btn = document.getElementById('exportBtn');
    btn.disabled = true;
    btn.textContent = 'Generating...';

    try {
        // Trigger download
        window.location.href = '/api/export';

        showMessage('Report generated successfully!', 'success');
    } catch (error) {
        showMessage('Error generating report', 'error');
    } finally {
        setTimeout(() => {
            btn.disabled = false;
            btn.textContent = 'Export Report';
        }, 3000);
    }
}

// Utility Functions

function openModal(modalId) {
    document.getElementById(modalId).style.display = 'block';
}

function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

function showMessage(message, type = 'info') {
    const container = document.getElementById('statusMessages');

    const messageDiv = document.createElement('div');
    messageDiv.className = `status-message ${type}`;
    messageDiv.textContent = message;

    container.appendChild(messageDiv);

    // Auto-remove after 5 seconds
    setTimeout(() => {
        messageDiv.remove();
    }, 5000);
}

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + Enter to submit forms
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        const googleModal = document.getElementById('googleModal');
        const scoringModal = document.getElementById('scoringModal');

        if (googleModal.style.display === 'block') {
            saveGoogleResponse();
        } else if (scoringModal.style.display === 'block') {
            submitScores();
        }
    }

    // Escape to close modals
    if (e.key === 'Escape') {
        closeModal('googleModal');
        closeModal('scoringModal');
    }
});
