# Copyright 2025 Harikrishna Srinivasan
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from Timetable.app import (check_login, login, logout,
                           nocache, page_not_found, sql)
from flask import Flask, render_template, redirect, request, send_file
from generate_hallplan import (generate_hallplan, process_hall,
                               process_schedule, process_slot)
from io import BytesIO
from jinja2 import FileSystemLoader
import os
import pandas as pd
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

app.before_request(lambda: check_login(login="logging_in"))


@app.route("/login", methods=["GET", "POST"])
@nocache
def logging_in():
    return login("upload")


@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        if not (request.files.get("slots") and request.files.get("schedules") \
                and request.files.get("classrooms")):
            return render_template("upload.html",
                                   error_message="Please upload all 3 files")

        _slots = request.files.get("slots")
        _schedules = request.files.get("schedules")
        _classrooms = request.files.get("classrooms")
        slots = process_slot(_slots)
        schedules = process_schedule(sql.cursor, _schedules,
                                     slots=slots, campus_id=2)
        classrooms = process_hall(sql.cursor, _classrooms, schedules, building_id=3)
        plan = generate_hallplan(sql.db_connector, sql.cursor, campus_id=2,
                                 schedules=schedules, halls=classrooms)

        # output = BytesIO()
        # with pd.ExcelWriter(output, engine="openpyxl") as writer:
        #     plan.to_excel(writer, sheet_name="attendance", index=False)
        # output.seek(0)

        # return send_file(
        #     output,
        #     as_attachment=True,
        #     download_name="attendance.xlsx",
        #     mimetype="application/vnd.openxmlformats-officedocument"
        #              ".spreadsheetml.sheet"
        # )

    return render_template("upload.html")


app.route("/logout")(logout)


app.errorhandler(404)(page_not_found)


if __name__ == "__main__":
    app.config.update(
        SESSION_COOKIE_SAMESITE="Strict",
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SECURE=True
    )
    app.run(host="0.0.0.0", port=5000, debug=False)
