import os
import sys
import unittest
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend_py.app import create_app
from backend_py.database import get_db


class SelfStudyApiTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.client = cls.app.test_client()
        conn = get_db()
        try:
            conn.execute(
                "DELETE FROM users WHERE email LIKE '%_test@example.com'"
            )
            conn.commit()
        finally:
            conn.close()

    def test_01_seed_courses(self):
        """Verify that courses and lessons are properly seeded."""
        response = self.client.get("/api/courses")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertGreaterEqual(len(data), 3)

        slugs = [c["slug"] for c in data]
        self.assertIn("java-foundations", slugs)
        self.assertIn("web-development", slugs)
        self.assertIn("git-and-github", slugs)

        # Check fields of course summary
        course = data[0]
        self.assertIn("id", course)
        self.assertIn("title", course)
        self.assertIn("category", course)
        self.assertIn("level", course)
        self.assertIn("durationHours", course)
        self.assertIn("lessonCount", course)
        self.assertFalse(course["enrolled"])

    def test_02_register_and_login(self):
        """Verify user registration and authentication flow."""
        reg_payload = {
            "name": "Alice Learner",
            "email": "alice_test@example.com",
            "password": "password123",
        }
        res_reg = self.client.post("/api/auth/register", json=reg_payload)
        self.assertEqual(res_reg.status_code, 201)
        self.assertIn("Registration successful", res_reg.get_json()["message"])

        # Duplicate registration should fail with 409
        res_dup = self.client.post("/api/auth/register", json=reg_payload)
        self.assertEqual(res_dup.status_code, 409)

        # Invalid login
        res_bad_login = self.client.post(
            "/api/auth/login",
            json={"email": "alice_test@example.com", "password": "wrongpassword"},
        )
        self.assertEqual(res_bad_login.status_code, 401)

        # Valid login
        res_login = self.client.post(
            "/api/auth/login",
            json={"email": "alice_test@example.com", "password": "password123"},
        )
        self.assertEqual(res_login.status_code, 200)
        login_data = res_login.get_json()
        self.assertIn("token", login_data)
        self.assertEqual(login_data["email"], "alice_test@example.com")
        self.assertEqual(login_data["name"], "Alice Learner")

    def test_03_course_details_locked_for_unenrolled(self):
        """Unenrolled users should see lesson titles but content should be null."""
        response = self.client.get("/api/courses/java-foundations")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()

        self.assertEqual(data["slug"], "java-foundations")
        self.assertFalse(data["enrolled"])
        self.assertGreater(len(data["lessons"]), 0)
        self.assertIsNone(data["lessons"][0]["content"])

    def test_04_learning_flow(self):
        """Test full flow: enroll -> see unlocked content -> complete lesson -> dashboard."""
        self.client.post(
            "/api/auth/register",
            json={"name": "Bob Learner", "email": "bob_test@example.com", "password": "password123"},
        )
        res_login = self.client.post(
            "/api/auth/login",
            json={"email": "bob_test@example.com", "password": "password123"},
        )
        token = res_login.get_json()["token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Check courses with token before enrollment
        res_courses = self.client.get("/api/courses", headers=headers)
        self.assertEqual(res_courses.status_code, 200)
        courses = res_courses.get_json()
        java_course = next(c for c in courses if c["slug"] == "java-foundations")
        self.assertFalse(java_course["enrolled"])

        # Enroll in java-foundations
        res_enroll = self.client.post("/api/courses/java-foundations/enroll", headers=headers)
        self.assertEqual(res_enroll.status_code, 201)
        self.assertEqual(res_enroll.get_json()["message"], "You are enrolled")

        # Get course detail; content should be unlocked
        res_detail = self.client.get("/api/courses/java-foundations", headers=headers)
        self.assertEqual(res_detail.status_code, 200)
        detail = res_detail.get_json()
        self.assertTrue(detail["enrolled"])
        first_lesson = detail["lessons"][0]
        self.assertIsNotNone(first_lesson["content"])
        self.assertFalse(first_lesson["completed"])

        # Complete the first lesson
        res_comp = self.client.post(f"/api/lessons/{first_lesson['id']}/complete", headers=headers)
        self.assertEqual(res_comp.status_code, 200)
        self.assertEqual(res_comp.get_json()["message"], "Lesson marked complete")

        # Check detail again; lesson should be completed and progressPercent > 0
        res_detail2 = self.client.get("/api/courses/java-foundations", headers=headers)
        detail2 = res_detail2.get_json()
        self.assertTrue(detail2["lessons"][0]["completed"])
        self.assertGreater(detail2["progressPercent"], 0)

        # Check dashboard
        res_dash = self.client.get("/api/me/dashboard", headers=headers)
        self.assertEqual(res_dash.status_code, 200)
        dash = res_dash.get_json()
        self.assertEqual(dash["name"], "Bob Learner")
        self.assertEqual(len(dash["courses"]), 1)
        self.assertEqual(dash["courses"][0]["slug"], "java-foundations")
        self.assertEqual(dash["courses"][0]["completedLessons"], 1)
        self.assertGreater(dash["courses"][0]["progressPercent"], 0)

    def test_05_cannot_complete_lesson_without_enrolling(self):
        """User cannot complete a lesson in a course they haven't enrolled in."""
        self.client.post(
            "/api/auth/register",
            json={"name": "Charlie", "email": "charlie_test@example.com", "password": "password123"},
        )
        res_login = self.client.post(
            "/api/auth/login",
            json={"email": "charlie_test@example.com", "password": "password123"},
        )
        token = res_login.get_json()["token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Get web-development course details without enrolling
        res_detail = self.client.get("/api/courses/web-development")
        first_lesson_id = res_detail.get_json()["lessons"][0]["id"]

        # Attempt to complete without enrolling
        res_comp = self.client.post(f"/api/lessons/{first_lesson_id}/complete", headers=headers)
        self.assertEqual(res_comp.status_code, 403)
        self.assertIn("Enroll in this course", res_comp.get_json()["message"])

    def test_06_lessons_unlock_in_sequence(self):
        """An enrolled learner must complete lessons in course order."""
        self.client.post(
            "/api/auth/register",
            json={"name": "Dana", "email": "dana_test@example.com", "password": "password123"},
        )
        login = self.client.post(
            "/api/auth/login",
            json={"email": "dana_test@example.com", "password": "password123"},
        )
        headers = {"Authorization": f"Bearer {login.get_json()['token']}"}

        self.client.post("/api/courses/web-development/enroll", headers=headers)
        detail = self.client.get("/api/courses/web-development", headers=headers).get_json()
        second_lesson = detail["lessons"][1]

        self.assertTrue(detail["lessons"][1]["locked"])
        response = self.client.post(
            f"/api/lessons/{second_lesson['id']}/complete",
            headers=headers,
        )
        self.assertEqual(response.status_code, 409)
        self.assertIn("previous", response.get_json()["message"])


if __name__ == "__main__":
    unittest.main()
