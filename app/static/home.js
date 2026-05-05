document.addEventListener("DOMContentLoaded", () => {
  syncAuthControls(Boolean(getToken()));
  markPageReady();
});