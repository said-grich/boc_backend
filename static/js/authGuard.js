
// Function to get the JWT token from localStorage
function getToken() {
    return localStorage.getItem('accessToken');
}

// Function to check if user is authenticated
function authGuard() {
    const token = getToken();
    
    const currentURL =window.location.pathname + window.location.search;
    console.log(token)
    if (!token) {
        if(currentURL!= "/"){
            window.location.href = '/';
            
        }
     
    }else{
        if(currentURL== "/"){
            window.location.href = '/search';
        }
    }
}

// Call authGuard on page load to protect the page
document.addEventListener('DOMContentLoaded', function() {
    authGuard(); 
});

function setAuthHeaders(xhr) {
    const token = getToken();
    if (token) {
        xhr.setRequestHeader('Authorization', 'Bearer ' + token);
    }
}
