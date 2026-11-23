# Self Study Platform

This project provides a full-stack learning platform with user registration, authentication (JWT), a seeded course catalog, course enrollment, lesson outlines and contents, lesson completion tracking, and a learner dashboard.

It can be run using either **Python (recommended for easy zero-setup local development)** or the original **Java / Spring Boot** stack.

---

## Running with Python (Zero-Setup & Recommended)

### 1. Requirements
- Python 3.10+
- Dependencies listed in `requirements.txt`

### 2. Install dependencies
```powershell
pip install -r requirements.txt
```

### 3. Run the application
From the project root:
```powershell
python app.py
```
*(or `python run.py`)*

The server automatically initializes the database (`self_study.db` via SQLite by default, or MySQL if configured), seeds sample courses and lessons, and starts listening on **`http://localhost:8080`**.

### 4. View in browser
- **Direct browser access**: Open **[http://localhost:8080](http://localhost:8080)** to access the frontend directly.
- **VS Code Live Server (optional)**: Open `frontend/index.html` on port 5500.

---

## Testing API Endpoints (PowerShell)

With the backend running, test the learning flow in PowerShell:

```powershell
# 1. Register a new user
$body = @{ name = "Test User"; email = "test@example.com"; password = "secret123" } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://localhost:8080/api/auth/register -ContentType "application/json" -Body $body

# 2. Log in and get JWT token
$login = @{ email = "test@example.com"; password = "secret123" } | ConvertTo-Json
$response = Invoke-RestMethod -Method Post -Uri http://localhost:8080/api/auth/login -ContentType "application/json" -Body $login

# 3. Browse courses
$headers = @{ Authorization = "Bearer $($response.token)" }
$courses = Invoke-RestMethod -Method Get -Uri http://localhost:8080/api/courses -Headers $headers
$course = $courses | Select-Object -First 1

# 4. Enroll in a course
Invoke-RestMethod -Method Post -Uri "http://localhost:8080/api/courses/$($course.slug)/enroll" -Headers $headers

# 5. Get course details and unlocked lessons
$detail = Invoke-RestMethod -Method Get -Uri "http://localhost:8080/api/courses/$($course.slug)" -Headers $headers

# 6. Complete the first lesson
Invoke-RestMethod -Method Post -Uri "http://localhost:8080/api/lessons/$($detail.lessons[0].id)/complete" -Headers $headers

# 7. Check learner dashboard
Invoke-RestMethod -Method Get -Uri http://localhost:8080/api/me/dashboard -Headers $headers
```

### Run Automated Unit Tests
```powershell
python -m unittest tests/test_api.py
```

---

## Alternative: Running with Java & Spring Boot

### Requirements
- Java 17
- Maven 3.8+
- Docker Desktop with Docker Compose

### Start the database
```powershell
docker compose up -d db
```

### Start the backend
From `backend`:
```powershell
mvn spring-boot:run
```

---

## API Summary

- `POST /api/auth/register` — Register a new learner account
- `POST /api/auth/login` — Sign in and receive a JWT bearer token
- `GET /api/courses` — Public course catalog (includes progress if token provided)
- `GET /api/courses/{slug}` — Course details and lesson outline (locks content unless enrolled)
- `POST /api/courses/{slug}/enroll` — Enroll the authenticated learner
- `POST /api/lessons/{lessonId}/complete` — Mark a lesson completed
- `GET /api/me/dashboard` — View enrolled courses and completion percentages
- `GET /api/health` — Verify the API and SQLite connection

---

## Professional Study Method

Every lesson follows a repeatable entry-level employee study loop:

1. **Understand the model** - explain the concept from memory before opening code.
2. **Study the core content** - read the lesson objectives and implementation notes.
3. **Build a small example** - turn the concept into working code or SQL.
4. **Test failure cases** - verify boundaries, invalid input, and error paths.
5. **Explain the tradeoff** - prepare to discuss why an approach was selected.
6. **Review and document** - write a README note, commit, or short demo.

Lessons unlock in order after enrollment. Completing each one builds a visible
learning history and a six-course portfolio curriculum covering Java, Python,
web development, Git/GitHub, SQL/databases, and professional software-engineering
habits.

## Recommended 12-Week Job-Entry Plan

| Week | Focus | Deliverable |
|---|---|---|
| 1-2 | Java Foundations | Inventory CLI, JUnit tests, README |
| 3-4 | Python Foundations | Flask API, database-backed tests |
| 5-6 | Web Development | Responsive accessible course website |
| 7 | SQL and Databases | Schema, migrations, analytics queries |
| 8 | Git and GitHub | Reviewed pull request and CI workflow |
| 9 | Software Engineering | Debugging, testing, security, and architecture notes |
| 10 | Portfolio Polish | Live demo, screenshots, architecture diagram |
| 11 | Interview Practice | Coding, debugging, STAR, and system-design mock sessions |
| 12 | Job Readiness | Tailored resume, GitHub profile, application tracker |

