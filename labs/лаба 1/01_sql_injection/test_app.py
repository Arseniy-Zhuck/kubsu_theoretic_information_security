import unittest
from app import app, attempt_login


class DemoTests(unittest.TestCase):
    def test_wrong_password(self):
        self.assertIsNone(attempt_login("admin", "wrong")[1])

    def test_regular_login(self):
        self.assertEqual(attempt_login("student", "student123")[1], ("student", "Студент"))

    def test_injection(self):
        self.assertEqual(attempt_login("admin' -- ", "anything")[1], ("admin", "Администратор"))

    def test_bad_sql(self):
        self.assertIsNotNone(attempt_login("'", "x")[2])

    def test_page(self):
        with app.test_client() as client:
            self.assertEqual(client.get("/", base_url="http://127.0.0.1:5050").status_code, 200)
            response = client.post("/", data={"username": "admin' -- ", "password": "x"},
                base_url="http://127.0.0.1:5050", headers={"Origin": "http://127.0.0.1:5050"})
            self.assertIn("Администратор", response.get_data(as_text=True))
            self.assertEqual(client.get("/", base_url="http://evil.example").status_code, 403)
            self.assertEqual(client.post("/", base_url="http://127.0.0.1:5050").status_code, 403)


if __name__ == "__main__":
    unittest.main()
