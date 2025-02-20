// Initialize Lucide icons
lucide.createIcons();

// Global storage for files and URLs
let selectedFiles = [];
let selectedUrls = [];

// Dark mode handling
function initializeDarkMode() {
    if (localStorage.theme === 'dark' || (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
        document.documentElement.classList.add('dark');
    } else {
        document.documentElement.classList.remove('dark');
    }
}

function toggleDarkMode() {
    const isDark = document.documentElement.classList.toggle('dark');
    localStorage.theme = isDark ? 'dark' : 'light';
    lucide.createIcons();
}

// Category selection handling
function selectCategory(category) {
    // Update button states
    document.getElementById('research-btn').classList.remove('border-red-500', 'border-blue-500');
    document.getElementById('technical-btn').classList.remove('border-red-500', 'border-blue-500');
    
    // Show input section
    document.getElementById('input-section').classList.remove('hidden');
    
    // Hide both input types initially
    document.getElementById('research-input').classList.add('hidden');
    document.getElementById('technical-input').classList.add('hidden');
    
    // Reset selections
    selectedFiles = [];
    selectedUrls = [];
    updateFilesList();
    updateUrlsList();
    
    // Update theme and show appropriate input
    if (category === 'research') {
        document.getElementById('research-btn').classList.add('border-red-500');
        document.getElementById('research-input').classList.remove('hidden');
        updateTheme('red');
    } else {
        document.getElementById('technical-btn').classList.add('border-blue-500');
        document.getElementById('technical-input').classList.remove('hidden');
        updateTheme('blue');
    }
    
    // Reset status and content
    document.getElementById('processing-status').innerHTML = '';
    document.getElementById('loading-indicator').style.display = 'none';
    document.getElementById('transcript-content').innerHTML = '';
    document.getElementById('generate-podcast').disabled = true;
    document.getElementById('audio-section').innerHTML = '';
}

function updateTheme(color) {
    const generateBtn = document.getElementById('generate-podcast');
    generateBtn.classList.remove('bg-gray-400', 'bg-red-600', 'bg-blue-600', 'hover:bg-red-700', 'hover:bg-blue-700');
    if (color === 'red') {
        generateBtn.classList.add('bg-red-600', 'hover:bg-red-700');
    } else {
        generateBtn.classList.add('bg-blue-600', 'hover:bg-blue-700');
    }
}

// File handling
document.getElementById('pdf-upload').addEventListener('change', function(e) {
    const files = Array.from(e.target.files);
    selectedFiles = selectedFiles.concat(files);
    updateFilesList();
});

function updateFilesList() {
    const filesList = document.getElementById('pdf-files-list');
    filesList.innerHTML = selectedFiles.map((file, index) => `
        <div class="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-700 rounded">
            <span class="text-sm text-gray-600 dark:text-gray-300">${file.name}</span>
            <button onclick="removeFile(${index})" class="text-red-500 hover:text-red-700">
                <i data-lucide="x" class="w-4 h-4"></i>
            </button>
        </div>
    `).join('');
    lucide.createIcons();
    document.getElementById('process-pdfs').disabled = selectedFiles.length === 0;
}

function removeFile(index) {
    selectedFiles.splice(index, 1);
    updateFilesList();
}

// URL handling
function addUrl() {
    const urlInput = document.getElementById('doc-url');
    const url = urlInput.value.trim();
    
    if (url && url.startsWith('http')) {
        selectedUrls.push(url);
        urlInput.value = '';
        updateUrlsList();
    }
}

function updateUrlsList() {
    const urlsList = document.getElementById('url-list');
    urlsList.innerHTML = selectedUrls.map((url, index) => `
        <div class="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-700 rounded">
            <span class="text-sm text-gray-600 dark:text-gray-300 truncate flex-1 mr-2">${url}</span>
            <button onclick="removeUrl(${index})" class="text-red-500 hover:text-red-700 flex-shrink-0">
                <i data-lucide="x" class="w-4 h-4"></i>
            </button>
        </div>
    `).join('');
    lucide.createIcons();
    document.getElementById('process-urls').disabled = selectedUrls.length === 0;
}

function removeUrl(index) {
    selectedUrls.splice(index, 1);
    updateUrlsList();
}

// Content processing
async function processFiles() {
    const formData = new FormData();
    selectedFiles.forEach(file => {
        formData.append('files', file);
    });
    
    try {
        const processingBtn = document.getElementById('process-pdfs');
        processingBtn.disabled = true;
        document.getElementById('loading-indicator').style.display = 'flex';
        
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        
        await handleProcessingResponse(response);
    } catch (error) {
        console.error('Error:', error);
        document.getElementById('processing-status').innerHTML = 
            '<span class="text-red-600 dark:text-red-400">Error processing files</span>';
    } finally {
        document.getElementById('process-pdfs').disabled = false;
        document.getElementById('loading-indicator').style.display = 'none';
    }
}

async function processUrls() {
    try {
        const processingBtn = document.getElementById('process-urls');
        processingBtn.disabled = true;
        document.getElementById('loading-indicator').style.display = 'flex';
        
        const response = await fetch('/upload', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                urls: selectedUrls
            })
        });
        
        await handleProcessingResponse(response);
    } catch (error) {
        console.error('Error:', error);
        document.getElementById('processing-status').innerHTML = 
            '<span class="text-red-600 dark:text-red-400">Error processing URLs</span>';
    } finally {
        document.getElementById('process-urls').disabled = false;
        document.getElementById('loading-indicator').style.display = 'none';
    }
}

async function handleProcessingResponse(response) {
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    if (data.transcript) {
        updateTranscript(data.transcript);
        document.getElementById('generate-podcast').disabled = false;
        document.getElementById('processing-status').innerHTML = 
            '<span class="text-green-600 dark:text-green-400">✓ Content processed successfully</span>';
    }
}

// Transcript handling
function updateTranscript(transcript) {
    const transcriptDiv = document.getElementById('transcript-content');
    const lines = transcript.split('\n').filter(line => line.trim() !== '');
    
    const html = lines.map((line, index) => {
        if (line.trim() === '') return '';
        
        // Alternate between speakers for each line
        const speaker = `Speaker ${(index % 2) + 1}`;
        
        // Check for tone indicators in parentheses
        const toneMatch = line.match(/\((.*?)\)/);
        const tone = toneMatch ? toneMatch[1] : '';
        const text = line.replace(/\((.*?)\)/, '').trim();
        
        const currentTheme = document.getElementById('research-btn').classList.contains('border-red-500') ? 'red' : 'blue';
        const mainColor = currentTheme === 'red' ? 'red' : 'blue';
        const altColor = currentTheme === 'red' ? 'orange' : 'indigo';
        
        return `
            <div class="mb-6">
                <div class="flex items-start gap-4">
                    <span class="text-sm font-medium text-${index % 2 === 0 ? mainColor : altColor}-600 dark:text-${index % 2 === 0 ? mainColor : altColor}-400 w-24 flex-shrink-0">
                        ${speaker}
                    </span>
                    <div class="flex-1 p-4 bg-${index % 2 === 0 ? mainColor : altColor}-50 dark:bg-${index % 2 === 0 ? mainColor : altColor}-900/10 rounded-lg">
                        ${tone ? `<div class="text-sm italic text-gray-500 dark:text-gray-400 mb-2">${tone}</div>` : ''}
                        <div class="text-gray-800 dark:text-gray-200" contenteditable="true">${text}</div>
                    </div>
                </div>
            </div>
        `;
    }).join('');
    
    transcriptDiv.innerHTML = html;
}

// Podcast generation
async function generatePodcast() {
    const transcriptDiv = document.getElementById('transcript-content');
    let transcript = '';
    
    // Collect transcript content
    transcriptDiv.querySelectorAll('.mb-6').forEach((segment, index) => {
        const speaker = `Speaker ${(index % 2) + 1}`;
        const tone = segment.querySelector('.italic')?.textContent.trim();
        const text = segment.querySelector('[contenteditable]').textContent.trim();
        
        transcript += `**${speaker}:**`;
        if (tone) transcript += ` (${tone})`;
        transcript += ` ${text}\n\n`;
    });
    
    // Show loading state
    const button = document.getElementById('generate-podcast');
    button.disabled = true;
    button.innerHTML = '<svg class="animate-spin h-5 w-5" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>';
    
    try {
        const response = await fetch('/generate-podcast', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ transcript: transcript })
        });

        if (!response.ok) throw new Error('Failed to generate podcast');

        const blob = await response.blob();
        const audioUrl = URL.createObjectURL(blob);
        document.getElementById('audio-section').innerHTML = `
            <audio controls class="w-full">
                <source src="${audioUrl}" type="audio/mpeg">
                Your browser does not support the audio element.
            </audio>
        `;
    } catch (error) {
        console.error('Error:', error);
        alert('Error generating podcast. Please try again.');
    } finally {
        // Reset button
        button.disabled = false;
        button.innerHTML = '<i data-lucide="mic" class="w-5 h-5"></i><span>Generate Podcast</span>';
        lucide.createIcons();
    }
}

// Add these to your script.js
function openRefineModal() {
    document.getElementById('refine-modal').classList.remove('hidden');
}

function closeRefineModal() {
    document.getElementById('refine-modal').classList.add('hidden');
}

async function refineTranscript() {
    const notes = document.getElementById('refinement-notes').value.trim();
    if (!notes) {
        alert('Please add some refinement notes');
        return;
    }

    const currentTranscript = collectCurrentTranscript();
    
    try {
        const response = await fetch('/refine-transcript', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                transcript: currentTranscript,
                refinement_notes: notes
            })
        });

        if (!response.ok) throw new Error('Failed to refine transcript');

        const data = await response.json();
        if (data.transcript) {
            updateTranscript(data.transcript);
            closeRefineModal();
            document.getElementById('refinement-notes').value = '';
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error refining transcript. Please try again.');
    }
}

function collectCurrentTranscript() {
    const transcriptDiv = document.getElementById('transcript-content');
    let transcript = '';
    
    transcriptDiv.querySelectorAll('.mb-6').forEach((segment, index) => {
        const speaker = `Speaker ${(index % 2) + 1}`;
        const tone = segment.querySelector('.italic')?.textContent.trim();
        const text = segment.querySelector('[contenteditable]').textContent.trim();
        
        transcript += `**${speaker}:**`;
        if (tone) transcript += ` (${tone})`;
        transcript += ` ${text}\n\n`;
    });
    
    return transcript;
}
// Initialize dark mode on load
initializeDarkMode();