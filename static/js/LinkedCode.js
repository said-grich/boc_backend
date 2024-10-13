document.addEventListener('DOMContentLoaded', () => {
    const spinner = document.getElementById('loading-spinner');

    // Show spinner function
    function showSpinner() {
        spinner.style.display = 'block';
    }

    // Hide spinner function
    function hideSpinner() {
        spinner.style.display = 'none';
    }

    // Registration
    document.getElementById('registrationForm').addEventListener('submit', function (event) {
        event.preventDefault(); // Prevent form from submitting normally
        showSpinner();  // Show the spinner when the form is submitted

        const username = document.getElementById('register_username').value;
        const email = document.getElementById('register_email').value;
        const password = document.getElementById('register_password').value;
        const confirmPassword = document.getElementById('register_confirm_password').value;

        fetch('/api/register/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username: username,
                email: email,
                password: password,
                confirm_password: confirmPassword,
            }),
        })
        .then(response => response.json())
        .then(data => {
            hideSpinner();  // Hide the spinner after the response
            if (data.username) {
                alert('Registration successful! You can now log in.');
                window.location.href = '/search/';  // Redirect to search page after successful registration
            } else {
                alert('Error: ' + JSON.stringify(data));
            }
        })
        .catch((error) => {
            hideSpinner();  // Hide the spinner in case of error
            console.error('Error:', error);
        });
    });

    // Login
    document.getElementById('loginForm').addEventListener('submit', function (event) {
        event.preventDefault(); // Prevent form from submitting normally
        showSpinner();  // Show the spinner when the form is submitted

        const email = document.getElementById('login_email').value;
        const password = document.getElementById('login_password').value;

        fetch('/api/login/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email: email,
                password: password,
            }),
        })
        .then(response => response.json())
        .then(data => {
            hideSpinner();  // Hide the spinner after the response
            if (data.access) {
                // Store tokens in local storage
                localStorage.setItem('accessToken', data.access);
                localStorage.setItem('refreshToken', data.refresh);
                alert('Login successful!');

                // Redirect to search page
                window.location.href = '/search/';  // Redirect to search page after successful login
            } else {
                alert('Error: ' + JSON.stringify(data));
            }
        })
        .catch((error) => {
            hideSpinner();  // Hide the spinner in case of error
            console.error('Error:', error);
        });
    });
});
