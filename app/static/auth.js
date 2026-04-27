function isValidEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

document.addEventListener("DOMContentLoaded", async () => {
  const form = document.querySelector("form");
  const messageEl = document.getElementById("message");

  if (!form) {
    return;
  }

  const redirected = await redirectIfAuthenticated();
  if (redirected) {
    return;
  }

  const flashMessage = consumeFlashMessage();
  if (flashMessage) {
    setMessage(messageEl, flashMessage, "success");
  }

  const mode = form.dataset.mode;

  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;
    const confirmPasswordInput = document.getElementById("confirm_password");

    if (!isValidEmail(email)) {
      setMessage(messageEl, "please enter a valid email address", "error");
      return;
    }

    if (password.length < 8) {
      setMessage(messageEl, "password must be at least 8 characters", "error");
      return;
    }

    if (confirmPasswordInput && password !== confirmPasswordInput.value) {
      setMessage(messageEl, "passwords do not match", "error");
      return;
    }

    const endpoint = mode === "register" ? "/register" : "/login";

    try {
      const { response, data } = await apiRequest(endpoint, {
        method: "POST",
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        setMessage(messageEl, data.detail || "could not complete request", "error");
        return;
      }

      if (data.access_token) {
        storeToken(data.access_token);
      }

      setMessage(messageEl, mode === "register" ? "account created" : "login successful", "success");
      form.reset();

      if (data.access_token) {
        window.location.href = "/calculations.html";
      }
    } catch {
      setMessage(messageEl, "could not reach server", "error");
    }
  });
});
