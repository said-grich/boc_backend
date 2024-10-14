// Function to fetch user profile data
function fetchUserProfile() {
    $.ajax({
        url: '/api/accounts/profile/', // The URL of your profile endpoint
        type: 'GET',
        beforeSend: function(xhr) {
            setAuthHeaders(xhr); 
          },
        success: function(data) {
            // Update HTML elements with user data
            $('#username').text(data.username);
            $('#email').text(data.email);
            
            // Update profile image if available
            if (data.profile_picture) {
                $('#profileImage').attr('src', data.profile_picture);
            }
        },
        error: function(xhr, status, error) {
            console.error('There was a problem with the AJAX request:', error);
        }
    });
}




// Call the function on page load
// document.addEventListener('DOMContentLoaded', fetchUserProfile);
// document.getElementById('savePictureButton').addEventListener('click', function () {
//     const imageUpload = document.getElementById('imageUpload').files[0];
//     const formData = new FormData();
//     formData.append('profile_picture', imageUpload);

//     fetch('/api/accounts/profile/update/', {
//         method: 'PUT', // Use PATCH if you want partial updates
//         headers: {
//             'Authorization': 'Bearer ' + localStorage.getItem('token'),
//         },
//         body: formData
//     })
//     .then(response => {
//         if (!response.ok) {
//             throw new Error('Network response was not ok');
//         }
//         return response.json();
//     })
//     .then(data => {
//         alert('Profile picture updated successfully!');
//         fetchUserProfile(); // Refresh profile data
//     })
//     .catch(error => {
//         console.error('There was a problem with the upload operation:', error);
//     });
// });



$(document).ready(function() {
    $('button[type="submit"]').on('click', function() {
        // Collecting the data from input fields
        const username = $('#usernameInput').val();
        const email = $('#emailInput').val();
        const password = $('#passwordInput').val();
        const confirmPassword = $('#confirmPasswordInput').val();

        // You can include additional validations here

        // Check if passwords match
        if (password !== confirmPassword) {
            alert("Passwords do not match!");
            return;
        }

        // Create the data object to send
        const data = {
            username: username,
            email: email,
            password: password,
        };

        $.ajax({
            url: '/api/accounts/profile/update/', // Adjust the URL as necessary
            method: 'PUT',
            contentType: 'application/json', // Set content type to JSON
            beforeSend: function(xhr) {
                setAuthHeaders(xhr); // Assuming setAuthHeaders is defined elsewhere
            },
            data: JSON.stringify(data), // The request payload
            success: function(response) {
                console.log('Profile updated successfully:', response);
                fetchUserProfile()
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.error('There was a problem with the AJAX operation:', textStatus, errorThrown);
            }
        });
    });
});


$(document).ready(function() {
    fetchUserProfile(); // Fetch user profile when the document is ready
});
