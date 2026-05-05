function isFiniteNumber(value) {
  return Number.isFinite(Number(value));
}

function validateCalculationPayload(a, b, type) {
  if (!isFiniteNumber(a) || !isFiniteNumber(b)) {
    return "a and b must be valid numbers";
  }

  if (!["Add", "Sub", "Multiply", "Divide"].includes(type)) {
    return "operation must be one of Add, Sub, Multiply, Divide";
  }

  if (type === "Divide" && Number(b) === 0) {
    return "division by zero is not allowed";
  }

  return "";
}

function renderList(container, calculations) {
  container.innerHTML = "";

  if (!calculations.length) {
    container.innerHTML = '<li class="list-empty">no calculations found</li>';
    return;
  }

  calculations.forEach((calculation) => {
    const item = document.createElement("li");
    item.className = "calc-item";
    item.innerHTML = `
      <strong>#${calculation.id}</strong>
      <span>${calculation.a} ${calculation.type} ${calculation.b} = ${calculation.result}</span>
      <button type="button" data-id="${calculation.id}" class="ghost-button small">Load ID</button>
    `;
    container.appendChild(item);
  });
}

document.addEventListener("DOMContentLoaded", () => {
  const messageEl = document.getElementById("calc-toast");
  const listEl = document.getElementById("calc-list");
  const readResultEl = document.getElementById("read-result");

  const addForm = document.getElementById("add-form");
  const readForm = document.getElementById("read-form");
  const editForm = document.getElementById("edit-form");
  const deleteForm = document.getElementById("delete-form");

  const refreshButton = document.getElementById("refresh-list");
  const logoutButton = document.getElementById("logout");

  async function browseCalculations() {
    const { response, data } = await apiRequest("/calculations", { method: "GET" });

    if (response.status === 401) {
      signOut();
      return;
    }

    if (!response.ok) {
      renderList(listEl, []);
      setMessage(messageEl, data.detail || "could not load calculations", "error");
      return;
    }

    renderList(listEl, data);
  }

  addForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const a = document.getElementById("add-a").value;
    const b = document.getElementById("add-b").value;
    const type = document.getElementById("add-type").value;

    const validationError = validateCalculationPayload(a, b, type);
    if (validationError) {
      setMessage(messageEl, validationError, "error");
      return;
    }

    const { response, data } = await apiRequest("/calculations", {
      method: "POST",
      body: JSON.stringify({ a: Number(a), b: Number(b), type }),
    });

    if (response.status === 401) {
      signOut();
      return;
    }

    if (!response.ok) {
      setMessage(messageEl, data.detail || "could not create calculation", "error");
      return;
    }

    addForm.reset();
    setMessage(messageEl, `created calculation #${data.id}`, "success");
    await browseCalculations();
  });

  readForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const id = Number(document.getElementById("read-id").value);

    if (!Number.isInteger(id) || id < 1) {
      setMessage(messageEl, "calculation id must be a positive integer", "error");
      return;
    }

    const { response, data } = await apiRequest(`/calculations/${id}`, { method: "GET" });

    if (response.status === 401) {
      signOut();
      return;
    }

    if (!response.ok) {
      readResultEl.textContent = "";
      setMessage(messageEl, data.detail || "could not load calculation", "error");
      return;
    }

    readResultEl.textContent = JSON.stringify(data, null, 2);
    setMessage(messageEl, `loaded calculation #${data.id}`, "success");
  });

  editForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const id = Number(document.getElementById("edit-id").value);
    const a = document.getElementById("edit-a").value;
    const b = document.getElementById("edit-b").value;
    const type = document.getElementById("edit-type").value;

    if (!Number.isInteger(id) || id < 1) {
      setMessage(messageEl, "calculation id must be a positive integer", "error");
      return;
    }

    const validationError = validateCalculationPayload(a, b, type);
    if (validationError) {
      setMessage(messageEl, validationError, "error");
      return;
    }

    const { response, data } = await apiRequest(`/calculations/${id}`, {
      method: "PUT",
      body: JSON.stringify({ a: Number(a), b: Number(b), type }),
    });

    if (response.status === 401) {
      signOut();
      return;
    }

    if (!response.ok) {
      setMessage(messageEl, data.detail || "could not update calculation", "error");
      return;
    }

    readResultEl.textContent = JSON.stringify(data, null, 2);
    setMessage(messageEl, `updated calculation #${data.id}`, "success");
    await browseCalculations();
  });

  deleteForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const id = Number(document.getElementById("delete-id").value);

    if (!Number.isInteger(id) || id < 1) {
      setMessage(messageEl, "calculation id must be a positive integer", "error");
      return;
    }

    const { response, data } = await apiRequest(`/calculations/${id}`, { method: "DELETE" });

    if (response.status === 401) {
      signOut();
      return;
    }

    if (!response.ok) {
      setMessage(messageEl, data.detail || "could not delete calculation", "error");
      return;
    }

    setMessage(messageEl, `deleted calculation #${id}`, "success");
    await browseCalculations();
  });

  refreshButton.addEventListener("click", async () => {
    await browseCalculations();
  });

  listEl.addEventListener("click", (event) => {
    const button = event.target.closest("button[data-id]");
    if (!button) {
      return;
    }

    const id = button.dataset.id;
    document.getElementById("read-id").value = id;
    document.getElementById("edit-id").value = id;
    document.getElementById("delete-id").value = id;
    setMessage(messageEl, `loaded #${id}`, "success");
  });

  logoutButton.addEventListener("click", () => {
    signOut();
  });

  syncAuthControls(Boolean(getToken()));

  requireAuth().then((allowed) => {
    if (!allowed) {
      return;
    }

    browseCalculations();
    markPageReady();
  });
});
