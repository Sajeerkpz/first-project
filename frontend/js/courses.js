document.addEventListener("DOMContentLoaded", async () => {
  const grid = document.getElementById("course-grid");
  const message = document.getElementById("courses-message");
  const search = document.getElementById("course-search");
  const categoryFilter = document.getElementById("category-filter");
  let courses = [];

  const render = () => {
    const query = search.value.trim().toLowerCase();
    const category = categoryFilter.value;
    const filtered = courses.filter((course) =>
      (!category || course.category === category)
      && (!query || `${course.title} ${course.description} ${course.category}`.toLowerCase().includes(query))
    );
    grid.replaceChildren();
    if (!filtered.length) {
      message.textContent = "No courses match those filters.";
      return;
    }

    message.textContent = `${filtered.length} course${filtered.length === 1 ? "" : "s"} available`;
    filtered.forEach((course) => {
      const card = document.createElement("article");
      card.className = "course-card";
      const meta = document.createElement("p");
      meta.className = "course-card-meta";
      meta.textContent = `${course.category} · ${course.level} · ${course.durationHours} hours`;
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
      link.textContent = course.enrolled ? `Continue · ${course.progressPercent}%` : "View course";
      footer.append(count, link);
      card.append(meta, title, description, footer);
      grid.append(card);
    });
  };

  search.addEventListener("input", render);
  categoryFilter.addEventListener("change", render);

  try {
    courses = await window.apiRequest("/courses");
    const categories = [...new Set(courses.map((course) => course.category))].sort();
    categories.forEach((category) => {
      const option = document.createElement("option");
      option.value = category;
      option.textContent = category;
      categoryFilter.append(option);
    });
    render();
  } catch (error) {
    message.textContent = error.message || "Could not load courses. Is the backend running?";
  }
});
