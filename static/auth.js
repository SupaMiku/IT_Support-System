/**
 * Authentication Helper Functions
 * Handles login, registration, and session management
 */

const API_BASE_URL = '/api';

/**
 * Show error message in form
 */
function showError(formElement, message) {
  let errorDiv = formElement.querySelector('.form-error');
  if (!errorDiv) {
    errorDiv = document.createElement('div');
    errorDiv.className = 'form-error';
    formElement.insertBefore(errorDiv, formElement.firstChild);
  }
  errorDiv.textContent = message;
  errorDiv.style.display = 'block';
}

/**
 * Hide error message
 */
function hideError(formElement) {
  const errorDiv = formElement.querySelector('.form-error');
  if (errorDiv) {
    errorDiv.style.display = 'none';
  }
}

/**
 * Set button loading state
 */
function setButtonLoading(button, isLoading) {
  if (isLoading) {
    button.disabled = true;
    button.dataset.originalText = button.textContent;
    button.textContent = '⏳ Processing...';
  } else {
    button.disabled = false;
    button.textContent = button.dataset.originalText || button.textContent;
  }
}

/**
 * Handle user login
 */
async function handleLogin(event) {
  event.preventDefault();
  
  const form = event.target;
  const button = form.querySelector('button[type="submit"]');
  const email = form.querySelector('input[type="email"]').value.trim();
  const password = form.querySelector('input[type="password"]').value;

  // Validation
  hideError(form);
  
  if (!email) {
    showError(form, '❌ Email is required');
    return;
  }
  if (!password) {
    showError(form, '❌ Password is required');
    return;
  }

  // API call
  setButtonLoading(button, true);
  
  try {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password })
    });

    const data = await response.json();

    if (!response.ok) {
      showError(form, `❌ ${data.error || 'Login failed'}`);
      setButtonLoading(button, false);
      return;
    }

    // Success
    showError(form, '');
    const successDiv = document.createElement('div');
    successDiv.className = 'form-success';
    successDiv.textContent = '✅ ' + data.message;
    form.insertBefore(successDiv, form.firstChild);
    
    // Redirect to dashboard after 1.5 seconds
    setTimeout(() => {
      window.location.href = '/dashboard';
    }, 1500);

  } catch (error) {
    showError(form, '❌ Network error: ' + error.message);
    setButtonLoading(button, false);
  }
}

/**
 * Handle user registration
 */
async function handleRegister(event) {
  event.preventDefault();
  
  const form = event.target;
  const button = form.querySelector('button[type="submit"]');
  const fullName = form.querySelector('input[type="text"]').value.trim();
  const email = form.querySelector('input[type="email"]').value.trim();
  const password = form.querySelector('input[type="password"]').value;

  // Validation
  hideError(form);
  
  if (!fullName) {
    showError(form, '❌ Name is required');
    return;
  }
  if (!email) {
    showError(form, '❌ Email is required');
    return;
  }
  if (!password) {
    showError(form, '❌ Password is required');
    return;
  }
  if (password.length < 6) {
    showError(form, '❌ Password must be at least 6 characters');
    return;
  }

  // API call
  setButtonLoading(button, true);
  
  try {
    const response = await fetch(`${API_BASE_URL}/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        full_name: fullName,
        email,
        password
      })
    });

    const data = await response.json();

    if (!response.ok) {
      showError(form, `❌ ${data.error || 'Registration failed'}`);
      setButtonLoading(button, false);
      return;
    }

    // Success
    hideError(form);
    const successDiv = document.createElement('div');
    successDiv.className = 'form-success';
    successDiv.textContent = '✅ ' + data.message + ' Redirecting to login...';
    form.insertBefore(successDiv, form.firstChild);
    
    // Redirect to login after 2 seconds
    setTimeout(() => {
      window.location.href = '/login';
    }, 2000);

  } catch (error) {
    showError(form, '❌ Network error: ' + error.message);
    setButtonLoading(button, false);
  }
}

/**
 * Initialize forms when DOM is ready
 */
document.addEventListener('DOMContentLoaded', function() {
  const loginForm = document.querySelector('.login-form');
  const registerForm = document.querySelector('.register-form');

  if (loginForm) {
    loginForm.addEventListener('submit', handleLogin);
  }

  if (registerForm) {
    registerForm.addEventListener('submit', handleRegister);
  }
});
