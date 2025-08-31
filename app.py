from Timetable.app import login, logout
from flask import Flask, render_template, request
from jinja2 import FileSystemLoader
import os
import secrets


app = Flask(__name__)
app.jinja_env.filters.pop("attr", None)
app.jinja_env.autoescape = True
app.secret_key = secrets.token_hex(16)

template_paths = [
    os.path.join(".", "templates"),
    os.path.join("Timetable", "templates")
]

app.jinja_env.loader = FileSystemLoader(template_paths)


@app.route("/", methods=["GET", "POST"])
def upload_page():
    if request.method == "POST":
        file1 = request.files.get("file1")
        file2 = request.files.get("file2")
        file3 = request.files.get("file3")
    return render_template("upload.html")


if __name__ == "__main__":
    app.config.update(
        SESSION_COOKIE_SAMESITE="Strict",
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SECURE=True
    )
    app.run(host="0.0.0.0", port=5001, debug=False)

