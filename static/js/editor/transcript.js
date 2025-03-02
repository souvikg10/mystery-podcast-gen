// Update the transcript display
function updateTranscript(transcript) {
    const transcriptDiv = document.getElementById('transcript-content');
    if (!transcriptDiv) return;

    // Parse transcript lines, filtering for speaker dialogues
    const speakerDialogueRegex = /(Speaker \d):\s*(?:\((.*?)\))?\s*(.+)/;
    const lines = transcript.split('\n')
        .map(line => line.trim())
        .filter(line => speakerDialogueRegex.test(line));

    const html = lines.map((line, index) => {
        const match = line.match(speakerDialogueRegex);
        if (!match) return '';

        const [, speaker, tone, text] = match;

        const currentTheme = document.getElementById('research-btn')?.classList.contains('border-red-500') ? 'red' : 'blue';
        const mainColor = currentTheme === 'red' ? 'red' : 'blue';
        const altColor = currentTheme === 'red' ? 'orange' : 'indigo';

        return `
            <div class="mb-6" data-original-line="${line}">
                <div class="flex items-start gap-4">
                    <span class="text-sm font-medium text-${index % 2 === 0 ? mainColor : altColor}-600 dark:text-${index % 2 === 0 ? mainColor : altColor}-400 w-24 flex-shrink-0">
                        ${speaker}
                    </span>
                    <div class="flex-1 p-4 bg-${index % 2 === 0 ? mainColor : altColor}-50 dark:bg-${index % 2 === 0 ? mainColor : altColor}-900/10 rounded-lg">
                        ${tone ? `<div class="text-sm italic text-gray-500 dark:text-gray-400 mb-2">${tone}</div>` : ''}
                        <div 
                            class="text-gray-800 dark:text-gray-200" 
                            contenteditable="true" 
                            data-original-text="${text}"
                        >${text}</div>
                    </div>
                </div>
            </div>
        `;
    }).join('');

    transcriptDiv.innerHTML = html;
}

// Open the refinement modal
function openRefineModal() {
    const modal = document.getElementById('refine-modal');
    if (modal) {
        modal.classList.remove('hidden');
    }
}

// Close the refinement modal
function closeRefineModal() {
    const modal = document.getElementById('refine-modal');
    if (modal) {
        modal.classList.add('hidden');
    }
}

// Process the transcript refinement
async function refineTranscript() {
    const notesElement = document.getElementById('refinement-notes');
    if (!notesElement) return;

    const notes = notesElement.value.trim();
    if (!notes) {
        alert('Please add some refinement notes');
        return;
    }

    const currentTranscript = AppState.currentTranscript;
    if (!currentTranscript) {
        alert('No transcript to refine');
        return;
    }

    try {
        const response = await fetch('/refine-transcript', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${access_token}`
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
            notesElement.value = '';
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error refining transcript. Please try again.');
    }
}