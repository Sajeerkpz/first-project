document.addEventListener("DOMContentLoaded", async () => {
  const slug = new URLSearchParams(window.location.search).get("slug");
  const message = document.getElementById("course-message");
  const detail = document.getElementById("course-detail");
  const enrollButton = document.getElementById("enroll-button");
  const token = localStorage.getItem("token");

  if (!slug) {
    message.textContent = "No course was selected.";
    return;
  }

  try {
    const course = await window.apiRequest(`/courses/${encodeURIComponent(slug)}`);
    document.title = `${course.title} | Self Study`;
    document.getElementById("course-title").textContent = course.title;
    document.getElementById("course-description").textContent = course.description;
    document.getElementById("course-meta").textContent =
      `${course.category} · ${course.level} · ${course.durationHours} hours · ${course.lessonCount} lessons`;
    document.getElementById("course-progress").textContent =
      course.enrolled ? `${course.progressPercent}% complete` : "";
    detail.hidden = false;
    message.textContent = "";

    enrollButton.hidden = !token || course.enrolled;
    document.getElementById("login-to-enroll").hidden = Boolean(token) || course.enrolled;
    document.getElementById("dashboard-link").hidden = !course.enrolled;
    enrollButton.addEventListener("click", async () => {
      enrollButton.disabled = true;
      try {
        await window.apiRequest(`/courses/${encodeURIComponent(slug)}/enroll`, { method: "POST" });
        window.location.reload();
      } catch (error) {
        message.textContent = error.message || "Could not enroll in the course.";
        enrollButton.disabled = false;
      }
    });

    const lessonList = document.getElementById("lesson-list");
    course.lessons.forEach((lesson) => {
      const item = document.createElement("li");
      item.className = "lesson-card";
      const heading = document.createElement("div");
      heading.className = "lesson-heading";
      const title = document.createElement("h3");
      title.textContent = `${lesson.position}. ${lesson.title}`;
      heading.append(title);
      if (lesson.completed) {
        const badge = document.createElement("span");
        badge.className = "completed-badge";
        badge.textContent = "Completed";
        heading.append(badge);
      }
      item.append(heading);

      if (course.enrolled && !lesson.locked) {
        const content = document.createElement("p");
        content.className = "lesson-content";
        content.textContent = lesson.content;
        item.append(content);
        if (!lesson.completed) {
          const complete = document.createElement("button");
          complete.className = "btn btn-outline";
          complete.type = "button";
          complete.textContent = "Mark complete";
          complete.addEventListener("click", async () => {
            complete.disabled = true;
            try {
              await window.apiRequest(`/lessons/${lesson.id}/complete`, { method: "POST" });
              window.location.reload();
            } catch (error) {
              message.textContent = error.message || "Could not update lesson progress.";
              complete.disabled = false;
            }
          });
          item.append(complete);
        }
      } else {
        const hint = document.createElement("p");
        hint.className = "lesson-content lesson-locked";
        hint.textContent = course.enrolled
          ? "Complete the previous lesson to unlock this lesson."
          : "Enroll in this course to open this lesson.";
        item.append(hint);
      }
      lessonList.append(item);
    });
  } catch (error) {
    message.textContent = error.message || "Could not load this course.";
  }
});
