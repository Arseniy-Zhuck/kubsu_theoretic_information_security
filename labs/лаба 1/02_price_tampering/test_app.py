import tempfile
import unittest
from pathlib import Path
import app as shop


class ShopTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.old = shop.DB_PATH
        shop.DB_PATH = Path(self.temp.name) / "shop.sqlite3"
        self.client = shop.app.test_client()

    def tearDown(self):
        shop.DB_PATH = self.old
        self.temp.cleanup()

    def post(self, path, **kw):
        return self.client.post(path, base_url="http://127.0.0.1:5051",
            headers={"Origin": "http://127.0.0.1:5051"}, **kw)

    def test_price_and_persistence(self):
        self.assertEqual(self.post("/buy", json={"product_id":"robot","price":10000}).status_code, 400)
        self.assertEqual(self.post("/buy", json={"product_id":"robot","price":1}).status_code, 200)
        with shop.connect() as db:
            self.assertEqual(db.execute("SELECT balance FROM wallet").fetchone()[0], 99)
            self.assertEqual(db.execute("SELECT paid FROM orders").fetchone()[0], 1)
        self.assertIn("Робот", self.client.get("/", base_url="http://127.0.0.1:5051").get_data(as_text=True))
        self.post("/reset")
        with shop.connect() as db:
            self.assertEqual(db.execute("SELECT balance FROM wallet").fetchone()[0], 100)
            self.assertEqual(db.execute("SELECT count(*) FROM orders").fetchone()[0], 0)

    def test_invalid_and_external(self):
        self.assertEqual(self.post("/buy", json={"product_id":"robot","price":-1}).status_code, 400)
        self.assertEqual(self.client.post("/buy", base_url="http://127.0.0.1:5051").status_code, 403)


if __name__ == "__main__":
    unittest.main()
