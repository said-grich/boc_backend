document.getElementById('resetPasswordForm').addEventListener('submit', function(event) {
    event.preventDefault();  // Prevent the default form submission

    var email = document.getElementById('email').value;  // Get the email input
    var messageDiv = document.getElementById('message'); // Message area for feedback

    if (email) {
        // Send the AJAX request to the backend
        var xhr = new XMLHttpRequest();
        xhr.open('POST', 'api/accounts/password-reset/', true);  // Your API endpoint for password reset
        xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');

        xhr.onload = function() {
            if (xhr.status === 200) {
                messageDiv.innerHTML = '<p style="color:green;">' + JSON.parse(xhr.responseText).message + '</p>';
            } else {
                var errorMessage = JSON.parse(xhr.responseText).error || 'Something went wrong. Please try again later.';
                messageDiv.innerHTML = '<p style="color:red;">' + errorMessage + '</p>';
            }
        };

        xhr.onerror = function() {
            messageDiv.innerHTML = '<p style="color:red;">Network error. Please check your connection.</p>';
        };

        // Send the request with email data
        xhr.send(JSON.stringify({ email: email }));
    } else {
        messageDiv.innerHTML = '<p style="color:red;">Please enter a valid email address.</p>';
    }
});
