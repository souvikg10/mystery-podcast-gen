/// Update the transcript display with improved parsing
function updateTranscript(transcript) {
    const transcriptDiv = document.getElementById('transcript-content');
    if (!transcriptDiv) return;

    // Improved regex that handles more variations of speaker patterns
    // This will match patterns like:
    // - "**Speaker 1:** Text"
    // - "Speaker 1: Text"
    // - "** Text" (will be attributed to previous speaker)
    // - "Text" (will be attributed to previous speaker if possible)
    const speakerDialogueRegex = /^\s*(?:\*\*)?(Speaker\s*\d+)(?:\*\*)?(?:\s*\(([^)]+)\))?:\s*(.+)/i;
    // Check for incomplete speaker tags (e.g., "** Text")
    const incompleteTagRegex = /^\s*\*\*\s+(.+)/;

    // Split transcript by lines
    const transcriptLines = transcript.split('\n').map(line => line.trim());

    const parsedLines = [];
    let currentSpeaker = null;
    let currentTone = null;
    let currentText = [];
    let speakerCount = 0;

    // Pre-process: Check if there's any valid speaker in the transcript
    const hasSpeakerFormat = transcriptLines.some(line => speakerDialogueRegex.test(line));

    // Process each line
    for (let i = 0; i < transcriptLines.length; i++) {
        const line = transcriptLines[i];
        if (!line) continue; // Skip empty lines
        // Try to match standard speaker format
        const speakerMatch = line.match(speakerDialogueRegex);
        // Try to match incomplete tag format (like "** Text")
        const incompleteMatch = !speakerMatch ? line.match(incompleteTagRegex) : null;

        if (speakerMatch) {
            // If we have accumulated text from a previous speaker, add it to results
            if (currentSpeaker && currentText.length > 0) {
                parsedLines.push({
                    speaker: currentSpeaker,
                    tone: currentTone,
                    text: currentText.join(' ')
                });
                currentText = [];
            }

            // Set the new current speaker and tone
            currentSpeaker = speakerMatch[1].replace(/\*\*/g, ''); // Remove any remaining asterisks
            currentTone = speakerMatch[2] || null;
            currentText.push(speakerMatch[3]);
            speakerCount++;
        } else if (incompleteMatch) {
            // If it's an incomplete tag, assign to previous speaker if possible
            // Or create a new speaker if this is the first dialogue
            if (!currentSpeaker) {
                currentSpeaker = "Speaker " + (speakerCount + 1);
                speakerCount++;
            }
            currentText.push(incompleteMatch[1]);
        } else if (line.startsWith("**") && line.includes("**")) {
            // Handle bold text that might be a speaker without proper format
            // Extract what's between ** and check if it has "Speaker" in it
            const boldText = line.match(/\*\*([^*]+)\*\*/);

            if (boldText && boldText[1].toLowerCase().includes('speaker')) {
                // Attempt to extract speaker number
                const speakerNumMatch = boldText[1].match(/speaker\s*(\d+)/i);
                if (speakerNumMatch) {
                    // Found a valid speaker, save previous speaker's text if exists
                    if (currentSpeaker && currentText.length > 0) {
                        parsedLines.push({
                            speaker: currentSpeaker,
                            tone: currentTone,
                            text: currentText.join(' ')
                        });
                        currentText = [];
                    }

                    // Set the new speaker
                    currentSpeaker = "Speaker " + speakerNumMatch[1];
                    currentTone = null;

                    // Get the text after the speaker
                    const textAfterSpeaker = line.substring(line.indexOf('**', boldText.index + 2) + 2).trim();
                    if (textAfterSpeaker.startsWith(':')) {
                        currentText.push(textAfterSpeaker.substring(1).trim());
                    } else {
                        currentText.push(textAfterSpeaker);
                    }
                    speakerCount++;
                }
                else {
                    // It's just bold text, treat as continuation
                    if (currentSpeaker) {
                        currentText.push(line);
                    } else {
                        // No current speaker, create a default one
                        currentSpeaker = "Speaker " + (speakerCount + 1);
                        currentText.push(line);
                        speakerCount++;
                    }
                }
            } else {
                // It's just bold text, treat as continuation
                if (currentSpeaker) {
                    currentText.push(line);
                } else {
                    // No current speaker, create a default one
                    currentSpeaker = "Speaker " + (speakerCount + 1);
                    currentText.push(line);
                    speakerCount++;
                }
            }
        } else if (currentSpeaker) {
            // If line doesn't match any pattern but we have a current speaker,
            // assume it's a continuation of their speech
            currentText.push(line);
        } else {
            // No current speaker, but we have text
            // Create a new default speaker
            currentSpeaker = "Speaker " + (speakerCount + 1);
            currentText.push(line);
            speakerCount++;
        }
    }

    // Add the last speaker's text
    if (currentSpeaker && currentText.length > 0) {
        parsedLines.push({
            speaker: currentSpeaker,
            tone: currentTone,
            text: currentText.join(' ')
        });
    }

    // If no valid speaker format was found, attempt to alternate speakers
    if (!hasSpeakerFormat && parsedLines.length > 1) {
        for (let i = 0; i < parsedLines.length; i++) {
            parsedLines[i].speaker = `Speaker ${(i % 2) + 1}`;
        }
    }

    // Determine the current theme
    const currentTheme = document.getElementById('research-btn')?.classList.contains('border-red-500') ? 'red' : 'blue';
    const mainColor = currentTheme === 'red' ? 'red' : 'blue';
    const altColor = currentTheme === 'red' ? 'orange' : 'indigo';

    // Generate HTML with the parsed lines
    const html = parsedLines.map((item, index) => {
        // Check if this is Speaker 1 or Speaker 2 (or any other number)
        const speakerNum = item.speaker.match(/speaker\s*(\d+)/i);
        const speakerIndex = speakerNum ? parseInt(speakerNum[1]) - 1 : index;

        return `
    <div class="mb-6" data-original-line="${encodeURIComponent(item.speaker + ': ' + (item.tone ? `(${item.tone}) ` : '') + item.text)}">
        <div class="flex items-start gap-4">
            <span class="text-sm font-medium text-${speakerIndex % 2 === 0 ? mainColor : altColor}-600 dark:text-${speakerIndex % 2 === 0 ? mainColor : altColor}-400 w-24 flex-shrink-0">
                ${item.speaker}
            </span>
            <div class="flex-1 p-4 bg-${speakerIndex % 2 === 0 ? mainColor : altColor}-50 dark:bg-${speakerIndex % 2 === 0 ? mainColor : altColor}-900/10 rounded-lg">
                ${item.tone ? `<div class="text-sm italic text-gray-500 dark:text-gray-400 mb-2">${item.tone}</div>` : ''}
                <div 
                    class="text-gray-800 dark:text-gray-200" 
                    contenteditable="true" 
                    data-original-text="${encodeURIComponent(item.text)}"
                >${item.text}</div>
            </div>
        </div>
    </div>
`;
    }).join('');

    // If no lines were parsed, provide a helpful message
    if (parsedLines.length === 0) {
        transcriptDiv.innerHTML = `
            <div class="p-4 bg-yellow-50 dark:bg-yellow-900/10 rounded-lg text-center">
                <p class="text-yellow-700 dark:text-yellow-400">No speaker dialogues found in the transcript.</p>
                <p class="text-gray-600 dark:text-gray-400 text-sm mt-2">
                    Transcript should contain lines in the format: <br>
                    <code class="bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded">Speaker 1: Your dialogue text here</code>
                </p>
            </div>
        `;
    } else {
        transcriptDiv.innerHTML = html;
    }

    // Enable audio generation if we have valid transcript content
    const generateAudioBtn = document.getElementById('generate-audio');
    if (generateAudioBtn) {
        generateAudioBtn.disabled = parsedLines.length === 0;
    }
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