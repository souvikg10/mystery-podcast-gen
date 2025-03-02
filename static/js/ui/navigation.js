// Switch between project sections (library, hosts, etc.)
function switchProjectSection(section) {
    // Update active tab styling
    document.querySelectorAll('nav button').forEach(btn => {
        btn.classList.remove('active-tab');
    });

    const sectionTab = document.getElementById(`${section}-tab`);
    if (sectionTab) {
        sectionTab.classList.add('active-tab');
    }

    if (section === 'library') {
        // Show library, hide other sections
        const librarySection = document.getElementById('library-section');
        const editorSection = document.getElementById('editor-section');

        if (librarySection) librarySection.classList.remove('hidden');
        if (editorSection) editorSection.classList.add('hidden');

        // Hide hosts section if it exists
        const hostsSection = document.getElementById('hosts-section');
        if (hostsSection) hostsSection.classList.add('hidden');

        // Load projects
        loadProjects();
    }
    else if (section === 'hosts') {
        // Hide other sections
        const librarySection = document.getElementById('library-section');
        const editorSection = document.getElementById('editor-section');

        if (librarySection) librarySection.classList.add('hidden');
        if (editorSection) editorSection.classList.add('hidden');

        // Show hosts section if it exists, or create it
        let hostsSection = document.getElementById('hosts-section');
        if (!hostsSection) {
            hostsSection = document.createElement('div');
            hostsSection.id = 'hosts-section';
            hostsSection.className = 'flex-1 p-6';
            hostsSection.innerHTML = `
                <div class="max-w-4xl mx-auto">
                    <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-6">Voice Hosts</h2>
                    <p class="text-gray-600 dark:text-gray-400 mb-6">
                        This feature is coming soon. You'll be able to customize podcast hosts' voices and personalities.
                    </p>
                    <div class="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
                        <div class="flex items-start">
                            <i data-lucide="info" class="w-5 h-5 text-blue-600 dark:text-blue-400 mr-3 mt-0.5"></i>
                            <p class="text-blue-600 dark:text-blue-400">
                                Stay tuned for updates to this feature.
                            </p>
                        </div>
                    </div>
                </div>
            `;
            const container = document.querySelector('.flex.flex-1.overflow-hidden');
            if (container) {
                container.appendChild(hostsSection);
                lucide.createIcons();
            }
        }

        hostsSection.classList.remove('hidden');
    }
}

// Switch between editor tabs (content, episodes)
function switchEditorTab(tab) {
    // Get all tabs and sections
    const tabs = document.querySelectorAll('.editor-tab');
    const contentSection = document.getElementById('content-editor-section');
    const episodesSection = document.getElementById('episodes-section');

    if (!tabs.length || !contentSection || !episodesSection) return;

    // Remove active class from all tabs
    tabs.forEach(t => t.classList.remove('active-editor-tab'));

    // Add active class to selected tab
    const selectedTab = document.getElementById(`${tab}-tab`);
    if (selectedTab) {
        selectedTab.classList.add('active-editor-tab');
    }

    if (tab === 'content') {
        contentSection.classList.remove('hidden');
        episodesSection.classList.add('hidden');
    } else {
        // Reset episode state when switching to episodes tab
        AppState.currentEpisode = null;
        AppState.currentTranscript = null;
        currentAudioData = null;

        contentSection.classList.add('hidden');
        episodesSection.classList.remove('hidden');
        loadEpisodes();
    }
}

// Toggle project menu dropdown
function toggleProjectMenu() {
    const dropdown = document.getElementById('project-dropdown');
    if (dropdown) {
        dropdown.classList.toggle('hidden');
    }
}