// Load projects from the server
async function loadProjects() {
    try {
        const response = await fetch('/user-projects', {
            headers: {
                'Authorization': `Bearer ${access_token}`
            },
        });
        if (!response.ok) {
            throw new Error('Failed to load projects');
        }
        const data = await response.json();

        // Set the current organization
        if (data.organization) {
            AppState.currentOrganization = data.organization;
        }

        // Set projects
        AppState.projects = data.projects || [];
        renderProjects();
    } catch (error) {
        console.error('Error loading projects:', error);
        alert('Failed to load projects. Please try again.');
    }
}

// Render projects in the library view
function renderProjects() {
    const projectsGrid = document.getElementById('projects-grid');
    if (!projectsGrid) return;

    // Clear existing projects
    projectsGrid.innerHTML = '';

    // Render each project
    AppState.projects.forEach(project => {
        const projectCard = document.createElement('div');
        projectCard.className = 'bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 border border-gray-200 dark:border-gray-700';

        projectCard.innerHTML = `
            <div class="flex flex-col space-y-2">
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white">${project.name}</h3>
                <span class="text-sm text-gray-500 dark:text-gray-400">
                    ${project.description}
                </span>
                <span class="text-sm text-gray-500 dark:text-gray-400">
                    Created: ${formatDate(project.created_at)}
                </span>
            </div>
            <div class="flex space-x-2">
                <button 
                    onclick="openProject('${project.id}')" 
                    class="px-3 py-1 bg-blue-500 text-white rounded-md hover:bg-blue-600">
                    Open
                </button>
                <button 
                    onclick="deleteProject('${project.id}')" 
                    class="px-3 py-1 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-md hover:bg-gray-300 dark:hover:bg-gray-600">
                    Delete
                </button>
            </div>
        `;

        projectsGrid.appendChild(projectCard);
    });
}

// Create a new project
async function createNewProject(name, description) {
    try {
        // Organization ID will be determined server-side based on the authenticated user
        const response = await fetch('/create-project', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${access_token}`
            },
            body: JSON.stringify({
                name: name,
                description: description || ''
            })
        });

        if (!response.ok) {
            throw new Error('Failed to create project');
        }

        const data = await response.json();
        const newProject = data.data;

        // Add to local state
        AppState.projects.push(newProject);

        // Open the newly created project
        openProject(newProject.id);

        // Re-render projects
        renderProjects();

        // Close modal
        closeCreateProjectModal();
    } catch (error) {
        console.error('Error creating project:', error);
        alert('Failed to create project. Please try again.');
    }
}

// Open a project in the editor
function openProject(projectId) {
    // Find the project
    const project = AppState.projects.find(p => p.id === projectId);

    if (project) {
        // Set current project
        AppState.currentProject = project;

        // Reset episode state
        AppState.currentEpisode = null;
        AppState.currentTranscript = null;
        currentAudioData = null;

        // Update project name in header
        updateProjectName(project.name);

        // Hide library section and show editor
        document.getElementById('library-section').classList.add('hidden');

        // Show editor with proper flex classes
        const editorSection = document.getElementById('editor-section');
        editorSection.classList.remove('hidden');
        editorSection.classList.add('flex', 'flex-col');

        // Reset transcript and audio
        document.getElementById('transcript-content').innerHTML = '';
        document.getElementById('audio-section').innerHTML = '';
        document.getElementById('generate-audio').disabled = true;
        document.getElementById('save-episode').disabled = true;

        // Switch to content editor tab by default
        switchEditorTab('content');
    }
}

// Delete a project
async function deleteProject(projectId) {
    // Confirm deletion
    if (confirm('Are you sure you want to delete this project?')) {
        try {
            const response = await fetch(`/delete-project/${projectId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${access_token}`
                },
            });

            if (!response.ok) {
                throw new Error('Failed to delete project');
            }

            // Remove project from local state
            AppState.projects = AppState.projects.filter(p => p.id !== projectId);

            // If the deleted project was the current project, clear it
            if (AppState.currentProject && AppState.currentProject.id === projectId) {
                AppState.currentProject = null;
                // Switch back to library view
                switchProjectSection('library');
            }

            // Re-render projects
            renderProjects();

        } catch (error) {
            console.error('Error deleting project:', error);
            alert('Failed to delete project. Please try again.');
        }
    }
}

// Update project name in UI
function updateProjectName(projectName) {
    const projectNameElement = document.getElementById('project-name');
    if (projectNameElement) {
        projectNameElement.textContent = projectName || 'Untitled Project';
    }
}