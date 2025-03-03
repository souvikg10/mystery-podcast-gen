// main.js - Entry point for loading all JavaScript modules
document.addEventListener('DOMContentLoaded', () => {
    // Load all necessary script files
    const scripts = [
        // Utils - load these first as they are used by other modules
        '/static/js/utils/helpers.js',
        '/static/js/utils/api.js',
        '/static/js/utils/file-upload.js',

        // UI components
        '/static/js/ui/theme.js',
        '/static/js/ui/navigation.js',
        '/static/js/ui/modals.js',

        // Editor components
        '/static/js/editor/transcript.js',
        '/static/js/editor/audio.js',
        '/static/js/editor/categories.js',

        // Project management
        '/static/js/projects/projects.js',
        '/static/js/projects/episodes.js',

        // Authentication
        '/static/js/auth/auth.js',
        '/static/js/auth/password.js',

        // Main app - load this last
        '/static/js/app.js'
    ];

    // Load scripts sequentially to ensure dependencies are met
    loadScripts(scripts, 0);
});

// Function to load scripts sequentially
function loadScripts(scripts, index) {
    if (index >= scripts.length) {
        // All scripts loaded, initialize the app
        console.log('All scripts loaded successfully');

        // Ensure file upload listeners are set up
        if (typeof initializeFileUploadListeners === 'function') {
            initializeFileUploadListeners();
        }

        if (typeof initializeApp === 'function') {
            initializeApp();
        }
        return;
    }

    const script = document.createElement('script');
    script.src = scripts[index];
    script.onload = () => {
        // Log each successfully loaded script
        console.log(`Loaded script: ${scripts[index]}`);

        // Load the next script
        loadScripts(scripts, index + 1);
    };
    script.onerror = (error) => {
        console.error(`Error loading script ${scripts[index]}:`, error);
        // Continue loading other scripts
        loadScripts(scripts, index + 1);
    };

    document.body.appendChild(script);
}

// Initialize app function (will be defined in app.js)
function initializeApp() {
    console.log('Application initialized');

    // Initialize Lucide icons
    lucide.createIcons();

    // Initialize various components
    initializeThemeToggle();
    initializeModalListeners();

    // Explicitly call file upload listeners initialization
    if (typeof initializeFileUploadListeners === 'function') {
        initializeFileUploadListeners();
    }

    // Check authentication
    const token = localStorage.getItem('auth_token');
    if (!token) {
        console.log("No token found, redirecting to login");
        window.location.href = '/login.html';
        return;
    }

    // Load initial data
    loadProjects();
}