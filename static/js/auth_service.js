document.addEventListener('DOMContentLoaded', () => {
    
  
    // Registration
    document.getElementById('registrationForm').addEventListener('submit', function (event) {
        event.preventDefault(); // Prevent form from submitting normally

        const username = document.getElementById('register_username').value;
        const email = document.getElementById('register_email').value;
        const password = document.getElementById('register_password').value;
        const confirmPassword = document.getElementById('register_confirm_password').value;
        $('#loading-spinner').show();
        fetch('api/accounts/register/', {
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
            $('#loading-spinner').hide();
            if (data.username) {
                alert('Registration successful! You can now log in.');
                window.location.href = '/search/';  // Redirect to search page after successful registration
            } else {
                alert('Error: ' + JSON.stringify(data));
            }
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    });




    // Login
    document.getElementById('loginForm').addEventListener('submit', function (event) {
        event.preventDefault(); 
    

        const email = document.getElementById('login_email').value;
        const password = document.getElementById('login_password').value;

        $('#loading-spinner').show();

        fetch('api/accounts/login/', {
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
            $('#loading-spinner').hide();
            if (data.access) {
                // Store tokens in local storage
                localStorage.setItem('accessToken', data.access);
                localStorage.setItem('refreshToken', data.refresh);
               
                // Redirect to search page
                window.location.href = '/search/';  // Redirect to search page after successful login
            } else {
                alert('Error: ' + JSON.stringify(data));
            }
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    });
});


function logout() {
    const refreshToken = localStorage.getItem('refreshToken');

    if (refreshToken) {
        $.ajax({
            url: '/api/accounts/logout/',
            method: 'POST',
            contentType: 'application/json',
            beforeSend: function(xhr) {
                setAuthHeaders(xhr); // Inject JWT token into the request headers
              },
            data: JSON.stringify({ refresh_token: refreshToken }),  // Send the refresh token as JSON
        })
        .done(function(response) {
            console.log("Logged out successfully");
            // Remove the tokens from localStorage
            localStorage.removeItem('accessToken');
            localStorage.removeItem('refreshToken');
            // Redirect to login page (or any other page)
            window.location.href = '/';
        })
        .fail(function(jqXHR, textStatus, errorThrown) {
            console.error("Logout failed:", textStatus, errorThrown);
        });
    } else {
        console.log("No refresh token found, redirecting to login.");
        window.location.href = '/';
    }
}
