// Global application state
const AppState = {
    currentOrganization: null,
    projects: [],
    currentProject: null,
    selectedFiles: [],
    selectedUrls: [],
    currentEpisode: null,
    currentTranscript: null
};

// Get authentication token
const access_token = localStorage.getItem("auth_token");

// Initialize application
document.addEventListener('DOMContentLoaded', () => {
    const token = localStorage.getItem('auth_token');

    if (!token) {
        console.log("No token found, redirecting to login");
        window.location.href = '/login.html';
        return;
    }

    // Initialize Lucide icons
    lucide.createIcons();

    // Initialize dark mode
    initializeDarkMode();

    // Load existing projects
    loadProjects();

    // Ensure we start in library view
    switchProjectSection('library');

    // Initialize event listeners
    initializeEventListeners();
});

// Set up event listeners that aren't tied to dynamically generated elements
function initializeEventListeners() {
    // File upload listeners
    const pdfUpload = document.getElementById('pdf-upload');
    if (pdfUpload) {
        pdfUpload.addEventListener('change', handleFileSelection);
    }

    // Password reset form
    const resetPasswordForm = document.getElementById('reset-password-form');
    if (resetPasswordForm) {
        resetPasswordForm.addEventListener('submit', handlePasswordResetSubmit);
    }
}