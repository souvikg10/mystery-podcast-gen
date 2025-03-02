// Load episodes for the current project
async function loadEpisodes() {
    if (!AppState.currentProject) return;

    try {
        const response = await fetch(`/episodes/${AppState.currentProject.id}`, {
            headers: {
                'Authorization': `Bearer ${access_token}`
            },
        });
        if (!response.ok) {
            throw new Error('Failed to load episodes');
        }

        const data = await response.json();
        if (data.status === 'success') {
            renderEpisodes(data.data);
        }
    } catch (error) {
        console.error('Error loading episodes:', error);
        alert('Failed to load episodes. Please try again.');
    }
}

// Render episodes in the episodes tab
function renderEpisodes(episodes) {
    const episodesContainer = document.querySelector('#episodes-section .divide-y');
    if (!episodesContainer) return;

    if (!episodes || episodes.length === 0) {
        episodesContainer.innerHTML = `
            <div class="p-8 text-center text-gray-500 dark:text-gray-400">
                No episodes found. Create your first episode in the Content Editor tab.
            </div>
        `;
        return;
    }

    episodesContainer.innerHTML = episodes.map(episode => `
        <div class="p-4 flex items-center justify-between hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors">
            <div class="flex items-center space-x-4">
                <div class="flex-1">
                    <h3 class="text-sm font-medium text-gray-900 dark:text-white">${episode.title}</h3>
                    <p class="text-sm text-gray-500 dark:text-gray-400">Created on ${formatDate(episode.created_at)}</p>
                </div>
            </div>
            <div class="flex items-center space-x-2">
                <button 
                    onclick="showTranscript('${episode.id}', ${JSON.stringify(episode.transcript).replace(/"/g, '&quot;')}, '${episode.audio_url})"
                    class="p-2 text-gray-500 hover:text-indigo-600 dark:text-gray-400 dark:hover:text-indigo-400 transition-colors" 
                    title="View Transcript">
                    <i data-lucide="file-text" class="w-5 h-5"></i>
                </button>
                <button 
                    onclick="deleteEpisode('${episode.id}')"
                    class="p-2 text-gray-500 hover:text-red-600 dark:text-gray-400 dark:hover:text-red-400 transition-colors" 
                    title="Delete Episode">
                    <i data-lucide="trash-2" class="w-5 h-5"></i>
                </button>
            </div>
        </div>
    `).join('');

    // Reinitialize Lucide icons
    lucide.createIcons();
}

// Show transcript and audio for an episode
function showTranscript(episodeId, transcript, audio_url) {
    // Set current episode
    AppState.currentEpisode = episodeId;
    AppState.currentTranscript = transcript;

    // Switch to content editor tab
    switchEditorTab('content');

    // Update the transcript content
    updateTranscript(transcript);
    playAudio(audio_url);

    // Enable buttons for editing existing episode
    document.getElementById('generate-audio').disabled = false;
    document.getElementById('save-episode').disabled = true;
}

// Delete an episode
async function deleteEpisode(episodeId) {
    if (!confirm('Are you sure you want to delete this episode?')) {
        return;
    }

    try {
        const response = await fetch(`/episodes/${episodeId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${access_token}`
            },
        });

        if (!response.ok) {
            throw new Error('Failed to delete episode');
        }

        // Reload episodes list
        await loadEpisodes();
    } catch (error) {
        console.error('Error deleting episode:', error);
        alert('Failed to delete episode. Please try again.');
    }
}

// Save the current episode
async function saveEpisode() {
    if (!currentAudioData || !AppState.currentProject) {
        return;
    }

    const saveButton = document.getElementById('save-episode');

    try {
        // Show loading state
        saveButton.disabled = true;
        saveButton.innerHTML = '<svg class="animate-spin h-5 w-5" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>';

        // Create FormData to send audio file
        const formData = new FormData();
        formData.append('audio', currentAudioData, 'episode.mp3');
        formData.append('project_id', AppState.currentProject.id);
        formData.append('transcript', AppState.currentTranscript);

        // If we're updating an existing episode, include its ID
        if (AppState.currentEpisode) {
            formData.append('episode_id', AppState.currentEpisode);
        }

        // Determine if this is a create or update operation
        const endpoint = AppState.currentEpisode ? `/update-episode/${AppState.currentEpisode}` : '/save-episode';
        const method = AppState.currentEpisode ? 'PUT' : 'POST';

        // Call the appropriate endpoint
        const response = await fetch(endpoint, {
            method: method,
            body: formData,
            headers: {
                'Authorization': `Bearer ${access_token}`
            },
        });

        if (!response.ok) throw new Error('Failed to save episode');

        const data = await response.json();

        // Show success message
        alert(AppState.currentEpisode ? 'Episode updated successfully!' : 'Episode saved successfully!');

        // Clear current audio data
        currentAudioData = null;

        // Disable save button
        saveButton.disabled = true;

        // Switch to episodes tab to show the new/updated episode
        switchEditorTab('episodes');

    } catch (error) {
        console.error('Error saving episode:', error);
        alert('Error saving episode. Please try again.');
    } finally {
        // Reset button
        saveButton.disabled = false;
        saveButton.innerHTML = '<i data-lucide="save" class="w-5 h-5"></i><span>Save Podcast Episode</span>';
        lucide.createIcons();
    }
}

// Save transcript to current project
function saveCurrentProjectTranscript(transcript) {
    if (AppState.currentProject) {
        // Add transcript to current project
        AppState.currentProject.transcripts = AppState.currentProject.transcripts || [];
        AppState.currentProject.transcripts.push({
            id: Date.now().toString(),
            content: transcript,
            createdAt: new Date().toISOString()
        });
    }
}