document.addEventListener("DOMContentLoaded", async () => {
  const grid = document.getElementById("featured-courses");
  const message = document.getElementById("featured-message");
  try {
    const courses = await window.apiRequest("/courses");
    message.textContent = courses.length ? "" : "No courses are available yet.";
    courses.slice(0, 3).forEach((course) => {
      const card = document.createElement("article");
      card.className = "course-card";
      const meta = document.createElement("p");
      meta.className = "course-card-meta";
      meta.textContent = `${course.category} · ${course.level}`;
      const title = document.createElement("h2");
      title.textContent = course.title;
      const description = document.createElement("p");
      description.textContent = course.description;
      const footer = document.createElement("div");
      footer.className = "course-card-footer";
      const count = document.createElement("span");
      count.textContent = `${course.lessonCount} lessons`;
      const link = document.createElement("a");
      link.className = "btn btn-primary";
      link.href = `course-detail.html?slug=${encodeURIComponent(course.slug)}`;
      link.textContent = "View course";
      footer.append(count, link);
      card.append(meta, title, description, footer);
      grid.append(card);
    });
  } catch (error) {
    message.textContent = error.message || "Could not load courses. Check that the backend is running.";
  }
});
