// Global storage for files and URLs
let selectedFiles = [];
let selectedUrls = [];

// Select content category (research or technical)
function selectCategory(category) {
    // Update button states
    const researchBtn = document.getElementById('research-btn');
    const technicalBtn = document.getElementById('technical-btn');

    if (!researchBtn || !technicalBtn) return;

    researchBtn.classList.remove('border-red-500', 'border-blue-500');
    technicalBtn.classList.remove('border-red-500', 'border-blue-500');

    // Show input section
    const inputSection = document.getElementById('input-section');
    if (inputSection) {
        inputSection.classList.remove('hidden');
    }

    // Hide both input types initially
    const researchInput = document.getElementById('research-input');
    const technicalInput = document.getElementById('technical-input');

    if (researchInput) researchInput.classList.add('hidden');
    if (technicalInput) technicalInput.classList.add('hidden');

    // Reset selections
    selectedFiles = [];
    selectedUrls = [];
    updateFilesList();
    updateUrlsList();

    // Update theme and show appropriate input
    if (category === 'research') {
        researchBtn.classList.add('border-red-500');
        if (researchInput) researchInput.classList.remove('hidden');
        updateTheme('red');
    } else {
        technicalBtn.classList.add('border-blue-500');
        if (technicalInput) technicalInput.classList.remove('hidden');
        updateTheme('blue');
    }

    // Reset status and content
    const processingStatus = document.getElementById('processing-status');
    const loadingIndicator = document.getElementById('loading-indicator');
    const transcriptContent = document.getElementById('transcript-content');
    const generateAudio = document.getElementById('generate-audio');
    const audioSection = document.getElementById('audio-section');

    if (processingStatus) processingStatus.innerHTML = '';
    if (loadingIndicator) loadingIndicator.style.display = 'none';
    if (transcriptContent) transcriptContent.innerHTML = '';
    if (generateAudio) generateAudio.disabled = true;
    if (audioSection) audioSection.innerHTML = '';
}

// Update theme color based on selected category
function updateTheme(color) {
    const generateBtn = document.getElementById('generate-audio');
    if (!generateBtn) return;

    generateBtn.classList.remove('bg-gray-400', 'bg-red-600', 'bg-blue-600', 'hover:bg-red-700', 'hover:bg-blue-700');
    if (color === 'red') {
        generateBtn.classList.add('bg-red-600', 'hover:bg-red-700');
    } else {
        generateBtn.classList.add('bg-blue-600', 'hover:bg-blue-700');
    }
}

// Process content based on selected category
async function processContent() {
    const researchBtn = document.getElementById('research-btn');

    if (researchBtn && researchBtn.classList.contains('border-red-500')) {
        await processFiles();
    } else {
        await processUrls();
    }
}