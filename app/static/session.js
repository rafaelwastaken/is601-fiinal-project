const LOGIN_URL = "/login.html";
const CALCULATIONS_URL = "/calculations.html";
const FLASH_MESSAGE_KEY = "auth_flash_message";

function setMessage(el, message, type) {
  if (!el) {
    return;
  }

  el.textContent = message;
  el.className = `message ${type || ""}`.trim();
}

function getToken() {
  return localStorage.getItem("jwt_token");
}

function storeToken(token) {
  localStorage.setItem("jwt_token", token);
}

function clearToken() {
  localStorage.removeItem("jwt_token");
}

function setFlashMessage(message) {
  sessionStorage.setItem(FLASH_MESSAGE_KEY, message);
}

function consumeFlashMessage() {
  const message = sessionStorage.getItem(FLASH_MESSAGE_KEY);
  if (message) {
    sessionStorage.removeItem(FLASH_MESSAGE_KEY);
  }

  return message;
}

async function apiRequest(path, options = {}) {
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };

  const token = getToken();
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(path, { ...options, headers });
  const data = await response.json().catch(() => ({}));
  return { response, data };
}

async function validateSession() {
  const token = getToken();
  if (!token) {
    return false;
  }

  const response = await fetch("/users/me", {
    headers: { Authorization: `Bearer ${token}` },
  });

  if (!response.ok) {
    clearToken();
    return false;
  }

  return true;
}

function syncAuthControls(isAuthenticated) {
  document.querySelectorAll("[data-auth-state='logged-in']").forEach((element) => {
    element.hidden = !isAuthenticated;
  });

  document.querySelectorAll("[data-auth-state='logged-out']").forEach((element) => {
    element.hidden = isAuthenticated;
  });
}

async function requireAuth() {
  const isAuthenticated = await validateSession();
  if (!isAuthenticated) {
    window.location.href = LOGIN_URL;
    return false;
  }

  syncAuthControls(true);
  return true;
}

async function redirectIfAuthenticated() {
  const isAuthenticated = await validateSession();
  if (isAuthenticated) {
    window.location.href = CALCULATIONS_URL;
    return true;
  }

  syncAuthControls(false);
  return false;
}

function signOut() {
  clearToken();
  window.location.href = LOGIN_URL;
}