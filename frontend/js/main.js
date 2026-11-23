document.addEventListener("DOMContentLoaded", () => {
  const themeToggle = document.getElementById("theme-toggle");
  const savedTheme = localStorage.getItem("theme");

  if (savedTheme === "dark") {
    document.body.classList.add("dark-mode");
  }

  if (themeToggle) {
    const updateThemeButton = () => {
      themeToggle.textContent = document.body.classList.contains("dark-mode") ? "☀️" : "🌙";
    };
    updateThemeButton();
    themeToggle.addEventListener("click", () => {
      document.body.classList.toggle("dark-mode");
      localStorage.setItem(
        "theme",
        document.body.classList.contains("dark-mode") ? "dark" : "light"
      );
      updateThemeButton();
    });
  }

  const token = localStorage.getItem("token");
  document.querySelectorAll(".guest-only").forEach((element) => {
    element.hidden = Boolean(token);
  });
  document.querySelectorAll(".auth-only").forEach((element) => {
    element.hidden = !token;
  });
  document.querySelectorAll(".signed-in-link").forEach((element) => {
    element.hidden = !token;
  });

  let user = null;
  try {
    user = JSON.parse(localStorage.getItem("user") || "null");
  } catch {
    localStorage.removeItem("user");
  }
  const welcome = document.getElementById("welcome-user");
  if (welcome && user?.name) {
    welcome.textContent = `Hi, ${user.name}`;
  }

  const logoutButton = document.getElementById("logout-btn");
  if (logoutButton) {
    logoutButton.addEventListener("click", () => {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      window.location.reload();
    });
  }
});
