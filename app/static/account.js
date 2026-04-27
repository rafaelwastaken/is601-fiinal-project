function validatePasswordChange(currentPassword, newPassword, confirmPassword) {
  if (currentPassword.length < 8 || newPassword.length < 8) {
    return "passwords must be at least 8 characters";
  }

  if (newPassword !== confirmPassword) {
    return "new passwords do not match";
  }

  return "";
}

document.addEventListener("DOMContentLoaded", async () => {
  const allowed = await requireAuth();
  if (!allowed) {
    return;
  }

  const logoutButton = document.getElementById("logout");
  const form = document.getElementById("password-form");
  const messageEl = document.getElementById("account-message");

  logoutButton.addEventListener("click", signOut);

  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const currentPassword = document.getElementById("current-password").value;
    const newPassword = document.getElementById("new-password").value;
    const confirmPassword = document.getElementById("confirm-password").value;

    const validationError = validatePasswordChange(currentPassword, newPassword, confirmPassword);
    if (validationError) {
      setMessage(messageEl, validationError, "error");
      return;
    }

    const { response, data } = await apiRequest("/users/me/password", {
      method: "POST",
      body: JSON.stringify({ current_password: currentPassword, new_password: newPassword }),
    });

    if (response.status === 401) {
      signOut();
      return;
    }

    if (!response.ok) {
      setMessage(messageEl, data.detail || "could not update password", "error");
      return;
    }

    clearToken();
    setFlashMessage("password updated. please sign in again.");
    window.location.href = "/login.html";
  });
});