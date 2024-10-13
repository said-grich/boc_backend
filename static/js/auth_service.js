
document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.querySelector('.sign-in form');
    const signupForm = document.querySelector('.sign-up form');
    const loginButton = document.getElementById('login');
    const registerButton = document.getElementById('register');
  
    // Toastr Configuration (Optional)
    toastr.options = {
      "closeButton": true,
      "debug": false,
      "newestOnTop": true,
      "progressBar": true,
      "positionClass": "toast-top-right",
      "preventDuplicates": true,
      "onclick": null,
      "showDuration": "300",
      "hideDuration": "1000",
      "timeOut": "5000",
      "extendedTimeOut": "1000",
      "showEasing": "swing",
      "hideEasing": "linear",
      "showMethod": "fadeIn",
      "hideMethod": "fadeOut"
    };
  
    // Function to handle signup
    signupForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      
      const name = signupForm.querySelector('input[placeholder="Name"]').value;
      const email = signupForm.querySelector('input[placeholder="Email"]').value;
      const password = signupForm.querySelector('input[placeholder="Password"]').value;
  
      const response = await fetch('/register/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username: name,
          email: email,
          password: password,
        }),
      });
  
      const data = await response.json();
      if (response.ok) {
        toastr.success('Signup successful! You can now log in.');
      } else {
        toastr.error(`Signup failed: ${data.detail || 'Something went wrong'}`);
      }
    });
  
    // Function to handle login
    loginForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      
      const email = loginForm.querySelector('input[placeholder="Email"]').value;
      const password = loginForm.querySelector('input[placeholder="Password"]').value;
  
      const response = await fetch('/login/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: email,
          password: password,
        }),
      });
  
      const data = await response.json();
      if (response.ok) {
        localStorage.setItem('access_token', data.access);
        localStorage.setItem('refresh_token', data.refresh);
        toastr.success('Login successful!');
        window.location.href = '/profile/';
      } else {
        toastr.error(`Login failed: ${data.detail || 'Invalid credentials'}`);
      }
    });
  
    // Toggle between signup and login views
    registerButton.addEventListener('click', () => {
      document.getElementById('container').classList.add('right-panel-active');
    });
  
    loginButton.addEventListener('click', () => {
      document.getElementById('container').classList.remove('right-panel-active');
    });
  });
  