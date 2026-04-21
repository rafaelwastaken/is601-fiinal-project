function setMessage(el, message, type) {
  el.textContent = message;
  el.className = `message ${type || ""}`.trim();
}

function isValidEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

async function postJson(url, body) {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  const data = await response.json().catch(() => ({}));
  return { response, data };
}

function storeToken(token) {
  localStorage.setItem("jwt_token", token);
}

function showToken(el, token) {
  el.textContent = token ? `token saved: ${token.slice(0, 24)}...` : "";
}

document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector("form");
  const messageEl = document.getElementById("message");
  const tokenEl = document.getElementById("token");

  if (!form) {
    return;
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
      const { response, data } = await postJson(endpoint, { email, password });

      if (!response.ok) {
        setMessage(messageEl, data.detail || "request failed", "error");
        return;
      }

      if (data.access_token) {
        storeToken(data.access_token);
        showToken(tokenEl, data.access_token);
      }

      const successText = mode === "register" ? "registration successful" : "login successful";
      setMessage(messageEl, successText, "success");
      form.reset();
    } catch {
      setMessage(messageEl, "could not reach server", "error");
    }
  });
});
