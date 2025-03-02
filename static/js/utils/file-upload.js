// Handle file selection from file input
function handleFileSelection(e) {
    const files = Array.from(e.target.files);
    selectedFiles = selectedFiles.concat(files);
    updateFilesList();
}

// Update the files list in the UI
function updateFilesList() {
    const filesList = document.getElementById('pdf-files-list');
    if (!filesList) return;

    filesList.innerHTML = selectedFiles.map((file, index) => `
        <div class="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-700 rounded">
            <span class="text-sm text-gray-600 dark:text-gray-300">${file.name}</span>
            <button onclick="removeFile(${index})" class="text-red-500 hover:text-red-700">
                <i data-lucide="x" class="w-4 h-4"></i>
            </button>
        </div>
    `).join('');

    lucide.createIcons();

    const processBtn = document.getElementById('process-pdfs');
    if (processBtn) {
        processBtn.disabled = selectedFiles.length === 0;
    }
}

// Remove a file from the selection
function removeFile(index) {
    selectedFiles.splice(index, 1);
    updateFilesList();
}

// Add a URL to the selection
function addUrl() {
    const urlInput = document.getElementById('doc-url');
    if (!urlInput) return;

    const url = urlInput.value.trim();

    if (url && url.startsWith('http')) {
        selectedUrls.push(url);
        urlInput.value = '';
        updateUrlsList();
    }
}

// Update the URLs list in the UI
function updateUrlsList() {
    const urlsList = document.getElementById('url-list');
    if (!urlsList) return;

    urlsList.innerHTML = selectedUrls.map((url, index) => `
        <div class="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-700 rounded">
            <span class="text-sm text-gray-600 dark:text-gray-300 truncate flex-1 mr-2">${url}</span>
            <button onclick="removeUrl(${index})" class="text-red-500 hover:text-red-700 flex-shrink-0">
                <i data-lucide="x" class="w-4 h-4"></i>
            </button>
        </div>
    `).join('');

    lucide.createIcons();

    const processBtn = document.getElementById('process-urls');
    if (processBtn) {
        processBtn.disabled = selectedUrls.length === 0;
    }
}

// Remove a URL from the selection
function removeUrl(index) {
    selectedUrls.splice(index, 1);
    updateUrlsList();
}

// Initialize file upload listeners
function initializeFileUploadListeners() {
    // URL form submission
    const urlForm = document.getElementById('url-form');
    if (urlForm) {
        urlForm.addEventListener('submit', (e) => {
            e.preventDefault();
            addUrl();
        });
    }

    // Add URL button
    const addUrlBtn = document.getElementById('add-url-btn');
    if (addUrlBtn) {
        addUrlBtn.addEventListener('click', addUrl);
    }
}