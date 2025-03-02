// Show create project modal
function openProjectModal() {
    const modal = document.getElementById('create-project-modal');
    if (modal) {
        modal.classList.remove('hidden');
        const input = document.getElementById('project-name-input');
        if (input) {
            input.focus();
            // Clear form
            const form = document.getElementById('create-project-form');
            if (form) {
                form.reset();
            }
        }
    }
}

// Close create project modal
function closeCreateProjectModal() {
    const modal = document.getElementById('create-project-modal');
    if (modal) {
        modal.classList.add('hidden');
    }
}

// Handle create project form submission
function handleCreateProjectSubmit(e) {
    e.preventDefault();
    const nameInput = document.getElementById('project-name-input');
    const descriptionInput = document.getElementById('project-description-input');

    if (!nameInput) return;

    const name = nameInput.value.trim();
    const description = descriptionInput ? descriptionInput.value.trim() : '';

    if (!name) {
        alert('Project name is required');
        return;
    }

    createNewProject(name, description);
}

// Initialize modal event listeners
function initializeModalListeners() {
    // Create project form submission
    const createProjectForm = document.getElementById('create-project-form');
    if (createProjectForm) {
        createProjectForm.addEventListener('submit', handleCreateProjectSubmit);
    }

    // Refine transcript form submission
    const refineForm = document.getElementById('refine-form');
    if (refineForm) {
        refineForm.addEventListener('submit', (e) => {
            e.preventDefault();
            refineTranscript();
        });
    }
}