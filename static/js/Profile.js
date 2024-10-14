// Function to fetch user profile data
function fetchUserProfile() {
    fetch('/profile/', {
        method: 'GET',
        headers: {
            'Authorization': 'Bearer ' + localStorage.getItem('token'), // Adjust if using a different token storage method
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        // Update HTML elements with user data
        document.getElementById('username').innerText = data.username;
        document.getElementById('email').innerText = data.email;
        
        // Update profile image if available
        if (data.profile_picture) {
            document.getElementById('profileImage').src = data.profile_picture;
        }
    })
    .catch(error => {
        console.error('There was a problem with the fetch operation:', error);
    });
}

// Call the function on page load
document.addEventListener('DOMContentLoaded', fetchUserProfile);
document.getElementById('savePictureButton').addEventListener('click', function () {
    const imageUpload = document.getElementById('imageUpload').files[0];
    const formData = new FormData();
    formData.append('profile_picture', imageUpload);

    fetch('/profile/update/', {
        method: 'PUT', // Use PATCH if you want partial updates
        headers: {
            'Authorization': 'Bearer ' + localStorage.getItem('token'),
        },
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        alert('Profile picture updated successfully!');
        fetchUserProfile(); // Refresh profile data
    })
    .catch(error => {
        console.error('There was a problem with the upload operation:', error);
    });
});
document.querySelector('button[type="submit"]').addEventListener('click', function() {
    // Collecting the data from input fields
    const username = document.getElementById('usernameInput').value;
    const email = document.getElementById('emailInput').value;
    const password = document.getElementById('passwordInput').value;
    const confirmPassword = document.getElementById('confirmPasswordInput').value;

    // You can include additional validations here

    // Create the data object to send
    const data = {
        username: username,
        email: email,
        password: password,
    };

    // Check if passwords match
    if (password !== confirmPassword) {
        alert("Passwords do not match!");
        return;
    }

    // Making a PUT request to update the profile
    fetch('/profile/update/', {
        method: 'PUT',
        headers: {
            'Authorization': 'Bearer ' + localStorage.getItem('token'), // Use the appropriate token method
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        console.log('Profile updated successfully:', data);
        alert("Profile updated successfully!");
    })
    .catch(error => {
        console.error('There was a problem with the fetch operation:', error);
    });
});