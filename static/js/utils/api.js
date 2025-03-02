// Process files and handle API response
async function processFiles() {
    const formData = new FormData();
    selectedFiles.forEach(file => {
        formData.append('files', file);
    });

    try {
        const processingBtn = document.getElementById('process-pdfs');
        if (processingBtn) processingBtn.disabled = true;

        const loadingIndicator = document.getElementById('loading-indicator');
        if (loadingIndicator) loadingIndicator.style.display = 'flex';

        const response = await fetch('/upload', {
            method: 'POST',
            body: formData,
            headers: {
                'Authorization': `Bearer ${access_token}`
            },
        });

        await handleProcessingResponse(response);
    } catch (error) {
        console.error('Error:', error);
        const processingStatus = document.getElementById('processing-status');
        if (processingStatus) {
            processingStatus.innerHTML =
                '<span class="text-red-600 dark:text-red-400">Error processing files</span>';
        }
    } finally {
        const processingBtn = document.getElementById('process-pdfs');
        if (processingBtn) processingBtn.disabled = false;

        const loadingIndicator = document.getElementById('loading-indicator');
        if (loadingIndicator) loadingIndicator.style.display = 'none';
    }
}

// Process URLs and handle API response
async function processUrls() {
    try {
        const processingBtn = document.getElementById('process-urls');
        if (processingBtn) processingBtn.disabled = true;

        const loadingIndicator = document.getElementById('loading-indicator');
        if (loadingIndicator) loadingIndicator.style.display = 'flex';

        const response = await fetch('/upload', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${access_token}`
            },
            body: JSON.stringify({
                urls: selectedUrls
            })
        });

        await handleProcessingResponse(response);
    } catch (error) {
        console.error('Error:', error);
        const processingStatus = document.getElementById('processing-status');
        if (processingStatus) {
            processingStatus.innerHTML =
                '<span class="text-red-600 dark:text-red-400">Error processing URLs</span>';
        }
    } finally {
        const processingBtn = document.getElementById('process-urls');
        if (processingBtn) processingBtn.disabled = false;

        const loadingIndicator = document.getElementById('loading-indicator');
        if (loadingIndicator) loadingIndicator.style.display = 'none';
    }
}

// Handle processing response from API
async function handleProcessingResponse(response) {
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    if (data.transcript) {
        // Store the original transcript
        AppState.currentTranscript = data.transcript;
        // Reset current episode since this is a new transcript
        AppState.currentEpisode = null;

        updateTranscript(data.transcript);

        const generateAudio = document.getElementById('generate-audio');
        if (generateAudio) generateAudio.disabled = false;

        const saveEpisode = document.getElementById('save-episode');
        if (saveEpisode) saveEpisode.disabled = true;

        const processingStatus = document.getElementById('processing-status');
        if (processingStatus) {
            processingStatus.innerHTML =
                '<span class="text-green-600 dark:text-green-400">✓ Content processed successfully</span>';
        }
    }
}