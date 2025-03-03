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

    // Ensure file upload listeners are set up
    if (typeof initializeFileUploadListeners === 'function') {
        initializeFileUploadListeners();
    }
});

// Set up event listeners that aren't tied to dynamically generated elements
function initializeEventListeners() {
    // Explicitly set up file upload listener
    const pdfUpload = document.getElementById('pdf-upload');
    if (pdfUpload) {
        // Remove any existing listeners first
        pdfUpload.removeEventListener('change', handleFileSelection);
        pdfUpload.addEventListener('change', handleFileSelection);
        console.log('PDF upload event listener added');
    }

    // Password reset form
    const resetPasswordForm = document.getElementById('reset-password-form');
    if (resetPasswordForm) {
        resetPasswordForm.addEventListener('submit', handlePasswordResetSubmit);
    }
}