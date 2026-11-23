document.addEventListener("DOMContentLoaded", async () => {
  const token = localStorage.getItem("token");
  if (!token) {
    window.location.replace("login.html");
    return;
  }

  const message = document.getElementById("dashboard-message");
  const grid = document.getElementById("dashboard-courses");
  const emptyState = document.getElementById("empty-dashboard");
  try {
    const dashboard = await window.apiRequest("/me/dashboard");
    document.getElementById("dashboard-title").textContent = `Welcome back, ${dashboard.name}`;
    message.textContent = dashboard.courses.length
      ? `${dashboard.courses.length} course${dashboard.courses.length === 1 ? "" : "s"} in progress`
      : "";
    emptyState.hidden = dashboard.courses.length > 0;
    dashboard.courses.forEach((course) => {
      const card = document.createElement("article");
      card.className = "course-card";
      const meta = document.createElement("p");
      meta.className = "course-card-meta";
      meta.textContent = `${course.category} · ${course.level}`;
      const title = document.createElement("h2");
      title.textContent = course.title;
      const progressText = document.createElement("p");
      progressText.textContent = `${course.completedLessons} of ${course.lessonCount} lessons completed`;
      const progress = document.createElement("progress");
      progress.max = 100;
      progress.value = course.progressPercent;
      progress.setAttribute("aria-label", `${course.progressPercent}% complete`);
      const footer = document.createElement("div");
      footer.className = "course-card-footer";
      const percentage = document.createElement("strong");
      percentage.textContent = `${course.progressPercent}%`;
      const link = document.createElement("a");
      link.className = "btn btn-primary";
      link.href = `course-detail.html?slug=${encodeURIComponent(course.slug)}`;
      link.textContent = "Continue learning";
      footer.append(percentage, link);
      card.append(meta, title, progressText, progress, footer);
      grid.append(card);
    });
  } catch (error) {
    message.textContent = error.message || "Could not load your dashboard.";
    if (error.message && /token|unauthorized|authentication/i.test(error.message)) {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      window.location.replace("login.html");
    }
  }
});
