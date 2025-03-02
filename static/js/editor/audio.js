// Store the current audio data
let currentAudioData = null;

// Play audio from URL
function playAudio(audioUrl) {
    const audioSection = document.getElementById('audio-section');
    if (!audioSection) return;

    audioSection.innerHTML = `
        <audio controls class="w-full h-10">
            <source src="${audioUrl}" type="audio/mpeg">
            Your browser does not support the audio element.
        </audio>
    `;
}

// Generate audio from the current transcript
async function generateAudio() {
    const button = document.getElementById('generate-audio');
    const saveButton = document.getElementById('save-episode');
    const transcriptDiv = document.getElementById('transcript-content');

    if (!button || !saveButton || !transcriptDiv) return;

    try {
        // Get the transcript from the editor
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
        button.disabled = true;
        button.innerHTML = '<svg class="animate-spin h-5 w-5" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>';

        // Call the generate-audio endpoint
        const response = await fetch('/generate-audio', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${access_token}` },
            body: JSON.stringify({ transcript: transcript })
        });

        if (!response.ok) throw new Error('Failed to generate podcast');

        // Get timing data from headers
        const timingData = JSON.parse(response.headers.get('X-Timing-Data'));
        window.transcriptTimings = timingData;

        // Create a blob URL from the streaming response
        const blob = await response.blob();
        const audioUrl = URL.createObjectURL(blob);

        // Create audio player
        playAudio(audioUrl);

        // Store the blob for later use
        currentAudioData = blob;

        // Enable save button
        saveButton.disabled = false;

    } catch (error) {
        console.error('Error:', error);
        alert('Error generating podcast. Please try again.');
    } finally {
        // Reset button
        button.disabled = false;
        button.innerHTML = '<i data-lucide="mic" class="w-5 h-5"></i><span>Generate Audio</span>';
        lucide.createIcons();
    }
}