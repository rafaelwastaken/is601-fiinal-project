const LOGIN_URL = "/login.html";
const CALCULATIONS_URL = "/calculations.html";
const FLASH_MESSAGE_KEY = "auth_flash_message";

document.body.classList.add("page-loading");

function dismissToast(toastEl) {
  if (!toastEl) {
    return;
  }

  if (toastEl._hideTimer) {
    clearTimeout(toastEl._hideTimer);
    toastEl._hideTimer = null;
  }

  toastEl.classList.remove("visible");
  setTimeout(() => {
    toastEl.remove();
  }, 300);
}

function setMessage(el, message, type) {
  if (!el) {
    return;
  }

  // toast queue mode for calculations page
  if (el.id === "calc-toast") {
    const toastEl = document.createElement("div");
    toastEl.className = `message toast ${type || ""}`.trim();
    toastEl.setAttribute("role", "status");

    const textEl = document.createElement("span");
    textEl.className = "toast-text";
    textEl.textContent = message;

    const closeBtn = document.createElement("button");
    closeBtn.type = "button";
    closeBtn.className = "toast-close";
    closeBtn.setAttribute("aria-label", "Dismiss notification");
    closeBtn.textContent = "x";
    closeBtn.addEventListener("click", () => {
      dismissToast(toastEl);
    });

    toastEl.append(textEl, closeBtn);
    // newest goes to top
    el.prepend(toastEl);

    requestAnimationFrame(() => {
      toastEl.classList.add("visible");
    });

    toastEl._hideTimer = setTimeout(() => {
      dismissToast(toastEl);
    }, 5000);

    return;
  }

  // clear any existing hide timers
  if (el._hideTimer) {
    clearTimeout(el._hideTimer);
    el._hideTimer = null;
  }

  if (el._clearTextTimer) {
    clearTimeout(el._clearTextTimer);
    el._clearTextTimer = null;
  }

  el.textContent = message;
  // apply semantic type class and show the message with animation
  el.className = `message ${type || ""}`.trim();
  // add visible class to trigger CSS transition
  el.classList.add("visible");

  // auto-hide after 5 seconds
  el._hideTimer = setTimeout(() => {
    el.classList.remove("visible");
    // after transition, clear the text
    el._clearTextTimer = setTimeout(() => {
      el.textContent = "";
      // reset to base message class (keep type cleared)
      el.className = "message";
      el._hideTimer = null;
      el._clearTextTimer = null;
    }, 300);
  }, 5000);
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

function markPageReady() {
  document.body.classList.remove("page-loading");
  document.body.classList.add("page-ready");
}