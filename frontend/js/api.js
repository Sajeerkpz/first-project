window.API_BASE_URL = "http://localhost:8080/api";

window.apiRequest = async (path, options = {}) => {
  const headers = new Headers(options.headers || {});
  const token = localStorage.getItem("token");
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }
  if (options.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(`${window.API_BASE_URL}${path}`, { ...options, headers });
  const contentType = response.headers.get("content-type") || "";
  const body = contentType.includes("application/json") ? await response.json() : await response.text();
  if (!response.ok) {
    const message = typeof body === "object" ? body.detail || body.message : body;
    throw new Error(message || `Request failed (${response.status})`);
  }
  return body;
};
