// app/static/js/script.js

// Function to display a notification
function showNotification(message, type) {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type}`;
    notification.textContent = message;
    document.body.appendChild(notification);
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Function to validate form inputs
function validateForm() {
    const forms = document.querySelectorAll('.needs-validation');
    Array.prototype.slice.call(forms).forEach(function (form) {
        form.addEventListener('submit', function (event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
                showNotification('Please fill out all required fields.', 'danger');
            }
            form.classList.add('was-validated');
        }, false);
    });
}

// Function to handle income and expense tracking
function handleTransactionForm() {
    const transactionForm = document.getElementById('transaction-form');
    if (transactionForm) {
        transactionForm.addEventListener('submit', function (event) {
            event.preventDefault();
            const amount = document.getElementById('amount').value;
            const category = document.getElementById('category').value;
            const date = document.getElementById('date').value;
            if (amount && category && date) {
                showNotification('Transaction added successfully!', 'success');
                // Reset form fields
                transactionForm.reset();
            } else {
                showNotification('Please fill out all fields.', 'danger');
            }
        });
    }
}

// Function to handle profile updates
function handleProfileUpdate() {
    const profileForm = document.getElementById('profile-form');
    if (profileForm) {
        profileForm.addEventListener('submit', function (event) {
            event.preventDefault();
            const username = document.getElementById('username').value;
            const email = document.getElementById('email').value;
            if (username && email) {
                showNotification('Profile updated successfully!', 'success');
                // Reset form fields
                profileForm.reset();
            } else {
                showNotification('Please fill out all fields.', 'danger');
            }
        });
    }
}

// Function to initialize tooltips (if using Bootstrap)
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.forEach(function (tooltipTriggerEl) {
        new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Document ready event listener
document.addEventListener("DOMContentLoaded", function () {
    console.log("JavaScript is loaded and ready.");

    // Initialize custom functions
    validateForm();
    handleTransactionForm();
    handleProfileUpdate();
    initializeTooltips();
});