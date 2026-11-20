"""Intentionally vulnerable local teaching shop. No real money."""
from contextlib import contextmanager
import sqlite3
from pathlib import Path
from flask import Flask, render_template, request, redirect

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 4096
DB_PATH = Path(__file__).parent / "data" / "shop.sqlite3"
PRODUCT = {"id": "robot", "name": "Робот-помощник", "price": 10000}


@contextmanager
def connect():
    DB_PATH.parent.mkdir(exist_ok=True)
    db = sqlite3.connect(DB_PATH)
    db.execute("CREATE TABLE IF NOT EXISTS wallet (id INTEGER PRIMARY KEY, balance INTEGER)")
    db.execute("INSERT OR IGNORE INTO wallet VALUES (1, 100)")
    db.execute("CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY, product TEXT, paid INTEGER)")
    db.commit()
    try:
        with db:
            yield db
    finally:
        db.close()


@app.before_request
def local_only():
    if request.host not in {"127.0.0.1:5051", "localhost:5051"}:
        return "Use http://127.0.0.1:5051", 403
    if request.method == "POST" and request.headers.get("Origin") not in {
        "http://127.0.0.1:5051", "http://localhost:5051"
    }:
        return "Local browser requests only", 403


@app.get("/")
def index():
    with connect() as db:
        balance = db.execute("SELECT balance FROM wallet WHERE id=1").fetchone()[0]
        orders = db.execute("SELECT id, product, paid FROM orders ORDER BY id DESC").fetchall()
    return render_template("index.html", product=PRODUCT, balance=balance, orders=orders)


@app.post("/buy")
def buy():
    try:
        data = request.get_json()
        if not isinstance(data, dict) or data.get("product_id") != PRODUCT["id"]:
            return {"message": "Неизвестный товар"}, 400
        # INTENTIONAL VULNERABILITY: the buyer chooses the price.
        price = data["price"]
        if type(price) is not int or price < 1 or price > 1000000:
            return {"message": "Цена должна быть положительным целым числом"}, 400
        with connect() as db:
            db.execute("BEGIN IMMEDIATE")
            balance = db.execute("SELECT balance FROM wallet WHERE id=1").fetchone()[0]
            if balance < price:
                return {"message": "Недостаточно монет"}, 400
            db.execute("UPDATE wallet SET balance=balance-? WHERE id=1", (price,))
            db.execute("INSERT INTO orders (product, paid) VALUES (?, ?)", (PRODUCT["name"], price))
        return {"message": f"Куплено за {price} монет! Обновите страницу."}
    except (KeyError, TypeError):
        return {"message": "Некорректный запрос"}, 400


@app.post("/reset")
def reset():
    with connect() as db:
        db.execute("UPDATE wallet SET balance=100 WHERE id=1")
        db.execute("DELETE FROM orders")
    return redirect("/")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5051, debug=False, use_reloader=False)
