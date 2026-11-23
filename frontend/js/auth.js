const API_URL = "http://localhost:8080/api/auth";

async function submitAuthForm(form, path, getPayload, onSuccess) {
  const message = document.getElementById("form-message");
  const submitButton = form.querySelector('button[type="submit"]');
  message.textContent = "";
  submitButton.disabled = true;

  try {
    const response = await fetch(`${API_URL}/${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(getPayload())
    });
    const body = await response.json().catch(() => ({}));

    if (!response.ok) {
      message.textContent = body.detail || body.message || "Request failed. Please try again.";
      return;
    }
    onSuccess(body);
  } catch (error) {
    message.textContent = "Could not reach the server. Check that the backend is running.";
  } finally {
    submitButton.disabled = false;
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const registerForm = document.getElementById("register-form");
  if (registerForm) {
    registerForm.addEventListener("submit", (event) => {
      event.preventDefault();
      submitAuthForm(
        registerForm,
        "register",
        () => ({
          name: document.getElementById("name").value.trim(),
          email: document.getElementById("email").value.trim(),
          password: document.getElementById("password").value
        }),
        () => {
          window.location.href = "login.html";
        }
      );
    });
  }

  const loginForm = document.getElementById("login-form");
  if (loginForm) {
    loginForm.addEventListener("submit", (event) => {
      event.preventDefault();
      submitAuthForm(
        loginForm,
        "login",
        () => ({
          email: document.getElementById("email").value.trim(),
          password: document.getElementById("password").value
        }),
        (body) => {
          localStorage.setItem("token", body.token);
          localStorage.setItem("user", JSON.stringify({ email: body.email, name: body.name }));
          window.location.href = "index.html";
        }
      );
    });
  }
});
