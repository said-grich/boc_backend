// Function to preview the uploaded image
function previewImage(event) {
    const reader = new FileReader();
    reader.onload = function() {
        const output = document.getElementById('profileImage');
        output.src = reader.result; // Set the image source to the uploaded file
    };
    reader.readAsDataURL(event.target.files[0]); // Read the uploaded file
}

// Event listener for the Upload button
document.getElementById('savePictureButton').addEventListener('click', function() {
    const imageFile = document.getElementById('imageUpload').files[0];
    if (!imageFile) {
        alert('Please select an image to upload.'); // Alert if no image is selected
        return;
    }
    // Simulate upload by showing an alert
    alert('Image uploaded successfully!'); // Notify the user of a successful "upload"
    // Here you could also reset the input if desired
    // document.getElementById('imageUpload').value = ""; // Clear the input
});