import re
import sqlite3
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify, g
from .models import User
from .security import (
    hash_password,
    verify_password,
    generate_token,
    login_required,
    optional_auth,
)
from .database import get_db

api_bp = Blueprint("api", __name__, url_prefix="/api")

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def now_utc_str() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def calculate_progress_percent(completed: int, total: int) -> int:
    return round((completed * 100.0) / total) if total > 0 else 0


@api_bp.route("/health", methods=["GET"])
def health():
    conn = get_db()
    try:
        conn.execute("SELECT 1").fetchone()
        return jsonify({"status": "healthy", "database": "connected"}), 200
    finally:
        conn.close()


# ==========================================
# Auth Endpoints
# ==========================================


@api_bp.route("/auth/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not name or len(name) > 100:
        return (
            jsonify({"message": "Name is required and must not exceed 100 characters.", "detail": "Invalid name."}),
            400,
        )

    if not email or len(email) > 254 or not EMAIL_REGEX.match(email):
        return (
            jsonify({"message": "A valid email address is required.", "detail": "Invalid email address."}),
            400,
        )

    if not password or len(password) < 8 or len(password) > 72:
        return (
            jsonify({"message": "Password must be between 8 and 72 characters.", "detail": "Invalid password length."}),
            400,
        )

    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        if cursor.fetchone():
            return (
                jsonify({"message": "Email already registered", "detail": "Email already registered"}),
                409,
            )

        hashed = hash_password(password)
        with conn:
            cursor.execute(
                "INSERT INTO users (name, email, password, role, created_at) VALUES (?, ?, ?, ?, ?)",
                (name, email, hashed, "ROLE_USER", now_utc_str()),
            )

        return (
            jsonify({"message": "Registration successful. Please log in."}),
            201,
        )
    finally:
        conn.close()


@api_bp.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return (
            jsonify({"message": "Invalid email or password", "detail": "Invalid email or password"}),
            401,
        )

    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        row = cursor.fetchone()
        user = User.from_row(row)

        if not user or not verify_password(password, user.password):
            return (
                jsonify({"message": "Invalid email or password", "detail": "Invalid email or password"}),
                401,
            )

        token = generate_token(user)
        return (
            jsonify({
                "token": token,
                "email": user.email,
                "name": user.name,
            }),
            200,
        )
    finally:
        conn.close()


# ==========================================
# Course Endpoints
# ==========================================


@api_bp.route("/courses", methods=["GET"])
@optional_auth
def list_courses():
    conn: sqlite3.Connection = g.db
    current_user: User | None = g.current_user
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM courses ORDER BY id ASC")
    courses = cursor.fetchall()

    enrolled_course_ids = set()
    if current_user:
        cursor.execute("SELECT course_id FROM enrollments WHERE user_id = ?", (current_user.id,))
        enrolled_course_ids = {row[0] for row in cursor.fetchall()}

    result = []
    for c in courses:
        cursor.execute("SELECT COUNT(*) FROM lessons WHERE course_id = ?", (c["id"],))
        total_lessons = cursor.fetchone()[0]

        is_enrolled = c["id"] in enrolled_course_ids
        completed_count = 0

        if current_user and is_enrolled:
            cursor.execute(
                """
                SELECT COUNT(*) FROM lesson_progress lp
                JOIN lessons l ON lp.lesson_id = l.id
                WHERE lp.user_id = ? AND l.course_id = ?
                """,
                (current_user.id, c["id"]),
            )
            completed_count = cursor.fetchone()[0]

        progress_pct = (
            calculate_progress_percent(completed_count, total_lessons)
            if (current_user and is_enrolled)
            else 0
        )

        result.append({
            "id": c["id"],
            "slug": c["slug"],
            "title": c["title"],
            "description": c["description"],
            "category": c["category"],
            "level": c["level"],
            "durationHours": c["duration_hours"],
            "lessonCount": total_lessons,
            "enrolled": is_enrolled,
            "completedLessons": completed_count,
            "progressPercent": progress_pct,
        })

    return jsonify(result), 200


@api_bp.route("/courses/<slug>", methods=["GET"])
@optional_auth
def course_detail(slug: str):
    conn: sqlite3.Connection = g.db
    current_user: User | None = g.current_user
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM courses WHERE slug = ?", (slug,))
    course = cursor.fetchone()
    if not course:
        return jsonify({"message": "Course not found", "detail": "Course not found"}), 404

    is_enrolled = False
    completed_lesson_ids = set()

    if current_user:
        cursor.execute(
            "SELECT id FROM enrollments WHERE user_id = ? AND course_id = ?",
            (current_user.id, course["id"]),
        )
        is_enrolled = cursor.fetchone() is not None

        if is_enrolled:
            cursor.execute(
                "SELECT lesson_id FROM lesson_progress WHERE user_id = ?",
                (current_user.id,),
            )
            completed_lesson_ids = {row[0] for row in cursor.fetchall()}

    cursor.execute(
        "SELECT * FROM lessons WHERE course_id = ? ORDER BY position ASC",
        (course["id"],),
    )
    lessons = cursor.fetchall()

    lesson_items = []
    completed_in_this_course = 0
    previous_completed = True
    for lesson in lessons:
        is_completed = lesson["id"] in completed_lesson_ids
        if is_completed:
            completed_in_this_course += 1
        is_locked = is_enrolled and not previous_completed
        if not is_enrolled:
            is_locked = True

        lesson_items.append({
            "id": lesson["id"],
            "title": lesson["title"],
            "position": lesson["position"],
            "content": lesson["content"] if is_enrolled and not is_locked else None,
            "completed": is_completed,
            "locked": is_locked,
        })
        previous_completed = is_completed

    total_lessons = len(lessons)
    progress_pct = (
        calculate_progress_percent(completed_in_this_course, total_lessons)
        if is_enrolled
        else 0
    )

    return (
        jsonify({
            "id": course["id"],
            "slug": course["slug"],
            "title": course["title"],
            "description": course["description"],
            "category": course["category"],
            "level": course["level"],
            "durationHours": course["duration_hours"],
            "enrolled": is_enrolled,
            "lessonCount": total_lessons,
            "lessons": lesson_items,
            "progressPercent": progress_pct,
        }),
        200,
    )


@api_bp.route("/courses/<slug>/enroll", methods=["POST"])
@login_required
def enroll(slug: str):
    conn: sqlite3.Connection = g.db
    current_user: User = g.current_user
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM courses WHERE slug = ?", (slug,))
    course = cursor.fetchone()
    if not course:
        return jsonify({"message": "Course not found", "detail": "Course not found"}), 404

    cursor.execute(
        "SELECT id FROM enrollments WHERE user_id = ? AND course_id = ?",
        (current_user.id, course["id"]),
    )
    existing = cursor.fetchone()

    if not existing:
        with conn:
            cursor.execute(
                "INSERT INTO enrollments (user_id, course_id, enrolled_at) VALUES (?, ?, ?)",
                (current_user.id, course["id"], now_utc_str()),
            )

    return jsonify({"message": "You are enrolled"}), 201


# ==========================================
# Learning & Progress Endpoints
# ==========================================


@api_bp.route("/lessons/<int:lesson_id>/complete", methods=["POST"])
@login_required
def complete_lesson(lesson_id: int):
    conn: sqlite3.Connection = g.db
    current_user: User = g.current_user
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM lessons WHERE id = ?", (lesson_id,))
    lesson = cursor.fetchone()
    if not lesson:
        return jsonify({"message": "Lesson not found", "detail": "Lesson not found"}), 404

    cursor.execute(
        "SELECT id FROM enrollments WHERE user_id = ? AND course_id = ?",
        (current_user.id, lesson["course_id"]),
    )
    is_enrolled = cursor.fetchone() is not None

    if not is_enrolled:
        return (
            jsonify({
                "message": "Enroll in this course before completing lessons",
                "detail": "Enroll in this course before completing lessons",
            }),
            403,
        )

    if lesson["position"] > 1:
        cursor.execute(
            """
            SELECT COUNT(*) FROM lessons l
            LEFT JOIN lesson_progress lp
              ON lp.lesson_id = l.id AND lp.user_id = ?
            WHERE l.course_id = ? AND l.position < ? AND lp.id IS NULL
            """,
            (current_user.id, lesson["course_id"], lesson["position"]),
        )
        incomplete_before = cursor.fetchone()[0]
        if incomplete_before:
            return (
                jsonify({
                    "message": "Complete the previous lessons first",
                    "detail": "Lessons must be completed in course order.",
                }),
                409,
            )

    cursor.execute(
        "SELECT id FROM lesson_progress WHERE user_id = ? AND lesson_id = ?",
        (current_user.id, lesson["id"]),
    )
    existing = cursor.fetchone()

    if not existing:
        with conn:
            cursor.execute(
                "INSERT INTO lesson_progress (user_id, lesson_id, completed_at) VALUES (?, ?, ?)",
                (current_user.id, lesson["id"], now_utc_str()),
            )

    return jsonify({"message": "Lesson marked complete"}), 200


@api_bp.route("/me/dashboard", methods=["GET"])
@login_required
def dashboard():
    conn: sqlite3.Connection = g.db
    current_user: User = g.current_user
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT c.id, c.slug, c.title, c.category, c.level, c.duration_hours
        FROM enrollments e
        JOIN courses c ON e.course_id = c.id
        WHERE e.user_id = ?
        ORDER BY e.enrolled_at DESC
        """,
        (current_user.id,),
    )
    enrolled_courses = cursor.fetchall()

    course_progress_list = []
    for c in enrolled_courses:
        cursor.execute("SELECT COUNT(*) FROM lessons WHERE course_id = ?", (c["id"],))
        total = cursor.fetchone()[0]

        cursor.execute(
            """
            SELECT COUNT(*) FROM lesson_progress lp
            JOIN lessons l ON lp.lesson_id = l.id
            WHERE lp.user_id = ? AND l.course_id = ?
            """,
            (current_user.id, c["id"]),
        )
        completed = cursor.fetchone()[0]
        pct = calculate_progress_percent(completed, total)

        course_progress_list.append({
            "id": c["id"],
            "slug": c["slug"],
            "title": c["title"],
            "category": c["category"],
            "level": c["level"],
            "durationHours": c["duration_hours"],
            "lessonCount": total,
            "completedLessons": completed,
            "progressPercent": pct,
        })

    return (
        jsonify({
            "name": current_user.name,
            "courses": course_progress_list,
        }),
        200,
    )
