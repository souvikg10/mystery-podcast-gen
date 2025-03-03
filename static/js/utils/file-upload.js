// Global variables for file and URL selection
let selectedFiles = [];
let selectedUrls = [];

// Handle file selection from file input
function handleFileSelection(e) {
    console.log('File selection event triggered');

    // Check if files were selected
    if (!e.target.files || e.target.files.length === 0) {
        console.warn('No files selected');
        return;
    }

    // Convert FileList to Array and filter PDF files
    const files = Array.from(e.target.files).filter(file =>
        file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf')
    );

    console.log(`Selected ${files.length} PDF files`);

    // Add new files to existing selection
    selectedFiles = [...selectedFiles, ...files];

    // Update UI
    updateFilesList();
}

// Update the files list in the UI
function updateFilesList() {
    const filesList = document.getElementById('pdf-files-list');
    const processBtn = document.getElementById('process-pdfs');

    if (!filesList) {
        console.warn('Files list container not found');
        return;
    }

    // Clear existing list
    filesList.innerHTML = '';

    // Populate list with selected files
    selectedFiles.forEach((file, index) => {
        const fileItem = document.createElement('div');
        fileItem.className = 'flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-700 rounded mb-2';
        fileItem.innerHTML = `
            <span class="text-sm text-gray-600 dark:text-gray-300 truncate max-w-[250px]">${file.name}</span>
            <button onclick="removeFile(${index})" class="text-red-500 hover:text-red-700 ml-2">
                <i data-lucide="x" class="w-4 h-4"></i>
            </button>
        `;
        filesList.appendChild(fileItem);
    });

    // Recreate Lucide icons
    if (typeof lucide !== 'undefined' && lucide.createIcons) {
        lucide.createIcons();
    }

    // Enable/disable process button
    if (processBtn) {
        processBtn.disabled = selectedFiles.length === 0;
        console.log(`Process button ${processBtn.disabled ? 'disabled' : 'enabled'}`);
    }
}

// Remove a file from the selection
function removeFile(index) {
    console.log(`Removing file at index ${index}`);
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

    // Recreate Lucide icons
    if (typeof lucide !== 'undefined' && lucide.createIcons) {
        lucide.createIcons();
    }

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

// Robust initialization function
function initializeFileUploadListeners() {
    console.log('Initializing file upload listeners');

    // PDF file input
    const pdfUpload = document.getElementById('pdf-upload');
    if (pdfUpload) {
        console.log('PDF upload input found');
        // Remove any existing listeners first
        pdfUpload.removeEventListener('change', handleFileSelection);
        pdfUpload.addEventListener('change', handleFileSelection);
    } else {
        console.warn('PDF upload input NOT found');
    }

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

// Expose functions globally for onclick handlers in HTML
window.handleFileSelection = handleFileSelection;
window.removeFile = removeFile;
window.addUrl = addUrl;
window.removeUrl = removeUrl;

// Call initialization on script load
initializeFileUploadListeners();