"""Intentionally vulnerable offline teaching example. Never deploy."""
import secrets
import sqlite3
from flask import Flask, render_template, request

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 4096
ALLOWED_HOSTS = {"127.0.0.1:5050", "localhost:5050"}


@app.before_request
def local_requests_only():
    if request.host not in ALLOWED_HOSTS:
        return "Use http://127.0.0.1:5050", 403
    if request.method == "POST" and request.headers.get("Origin") not in {
        "http://127.0.0.1:5050", "http://localhost:5050"
    }:
        return "Local browser requests only", 403


def attempt_login(username, password):
    # Fictional disposable credentials; deliberately simplified plaintext schema.
    db = sqlite3.connect(":memory:")
    try:
        db.execute("CREATE TABLE users (username TEXT, password TEXT, role TEXT)")
        db.executemany("INSERT INTO users VALUES (?, ?, ?)", [
            ("admin", secrets.token_urlsafe(24), "Администратор"),
            ("student", "student123", "Студент"),
        ])
        query = "SELECT username, role FROM users WHERE username = '" + username + "' AND password = '" + password + "'"
        try:
            row = db.execute(query).fetchone()
            return query, row, None
        except sqlite3.Error:
            return query, None, "Ошибка SQL: запрос получился некорректным."
    finally:
        db.close()


@app.route("/", methods=["GET", "POST"])
def index():
    query = row = error = None
    if request.method == "POST":
        username = request.form.get("username", "")[:200]
        password = request.form.get("password", "")[:200]
        query, row, error = attempt_login(username, password)
    return render_template("index.html", query=query, row=row, error=error)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5050, debug=False, use_reloader=False)
