// Password reset modal functions
function openResetPasswordModal() {
    document.getElementById('reset-password-modal').classList.remove('hidden');
    document.getElementById('current-password').focus();
    // Clear form
    document.getElementById('reset-password-form').reset();
}

function closeResetPasswordModal() {
    document.getElementById('reset-password-modal').classList.add('hidden');
}

// Function to handle password reset
async function resetPassword(currentPassword, newPassword) {
    try {
        const response = await fetch('/auth/reset-password', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${access_token}`
            },
            body: JSON.stringify({
                current_password: currentPassword,
                new_password: newPassword
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Password reset failed');
        }

        // Reset successful
        alert('Password has been reset successfully.');
        closeResetPasswordModal();
    } catch (error) {
        console.error('Password reset error:', error);
        alert(error.message || 'Password reset failed. Please try again.');
    }
}

// Handle form submission for password reset
function handlePasswordResetSubmit(e) {
    e.preventDefault();

    const currentPassword = document.getElementById('current-password').value;
    const newPassword = document.getElementById('new-password').value;
    const confirmPassword = document.getElementById('confirm-password').value;

    // Validate passwords
    if (newPassword !== confirmPassword) {
        alert('New passwords do not match.');
        return;
    }

    if (newPassword.length < 8) {
        alert('New password must be at least 8 characters long.');
        return;
    }

    // Reset password
    resetPassword(currentPassword, newPassword);
}