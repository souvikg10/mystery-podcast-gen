// Logout function
async function logoutUser() {
    if (confirm('Are you sure you want to log out?')) {
        try {
            // Call logout endpoint
            await fetch('/auth/signout', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${access_token}`
                }
            });

            // Clear local storage
            localStorage.removeItem('auth_token');

            // Redirect to login page
            window.location.href = '/login.html';
        } catch (error) {
            console.error('Logout error:', error);

            // Even if the API call fails, we'll still log out locally
            localStorage.removeItem('auth_token');
            window.location.href = '/login.html';
        }
    }
}