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


from Timetable.app import (about, check_login, login, logout,
                           nocache, page_not_found, sql)
from Timetable.typehints import Response
from datetime import datetime
from flask import Flask, render_template, request
from generate_hallplan import (generate_hallplan, process_hall,
                               process_schedule, process_slot)
from jinja2 import FileSystemLoader
import fetch_data
import os
import pandas as pd
import secrets


app = Flask(__name__)
app.jinja_env.filters.pop("attr", None)
app.jinja_env.autoescape = True
app.secret_key = secrets.token_hex(16)
table: list[dict] = []
dates: list[str] = []
slots: list[int] = []

template_paths = [
    os.path.join(".", "templates"),
    os.path.join("Timetable", "templates")
]

app.jinja_env.loader = FileSystemLoader(template_paths)

app.before_request(check_login)


app.route("/login", methods=["GET", "POST"])(nocache(login))


@app.route("/home")
@app.route("/")
def index() -> str:
    return render_template("./index.html")


app.route("/about")(about)


@app.route("/upload")
def upload() -> Response | str:
    table.clear()
    return render_template("./upload.html")


def _hallplan(plan: pd.DataFrame) -> None:
    def to_fmt(date: datetime) -> str:
        return date.strftime("%d/%m/%Y")

    for date_slot, data in plan.groupby(["Date", "SlotNo"]):
        date, slot_no = date_slot
        section_groups = data.groupby(["Year", "Degree", "Stream", "Section"])
        for _section, cls_stds in section_groups:
            year, degree, stream, section = _section
            description = f"{year} {degree} "
            if stream != "NULL":
                description += f"({stream}) "

            description += f"{section} "
            halls = cls_stds.groupby("RoomNo").agg(
                _min=("RegNo", "min"),
                _max=("RegNo", "max")
            ).sort_values("_min")

            table.append({
                "date": to_fmt(date),
                "slot_no": int(slot_no),
                "course_code": cls_stds.iloc[0]["CourseCode"],
                "description": description,
                "halls": {hall: f"{reg_no['_min']}-{reg_no['_max']}"
                          for hall, reg_no in halls.iterrows()}
            })
    slots.extend(plan["SlotNo"].unique().tolist())
    dates.extend(plan["Date"].apply(to_fmt).unique().tolist())


@app.route("/hallplan", methods=["GET", "POST"])
def hallplan() -> str:
    if not (sql.db_connector and sql.cursor):
        return render_template("./failed.html",
                               reason="Unable to authenticate!")

    if request.method == "GET":
        plan = fetch_data.get_attendance(sql.cursor, fmt="pandas")
        if isinstance(plan, pd.DataFrame):
            _hallplan(plan)

    if table:
        _date = request.form.get("date")
        _slot = request.form.get("slot")
        t1 = table
        if _date:
            t1 = [t for t in t1 if str(t["date"]) == _date]
        if _slot:
            t1 = [t for t in t1 if str(t["slot_no"]) == _slot]
        return render_template("./hallplan.html", table=t1,
                               dates=dates, slots=slots)

    if request.method == "POST":
        if not (request.files.get("slots") and request.files.get("schedules")
                and request.files.get("classrooms")):
            return render_template("./upload.html",
                                   error_message="Please upload all 3 files")

        __slots = request.files["slots"]
        _schedules = request.files["schedules"]
        _classrooms = request.files["classrooms"]
        _slots = process_slot(sql.db_connector, sql.cursor, __slots)
        schedules = process_schedule(sql.cursor, _schedules,
                                     slots=_slots, campus_id=2)
        classrooms = process_hall(sql.cursor, _classrooms, building_id=3)
        plan = generate_hallplan(sql.db_connector, sql.cursor,
                                 schedules=schedules, halls=classrooms)
        _hallplan(plan)
    return render_template("./hallplan.html", table=table,
                           dates=dates, slots=slots)


@app.route("/attendance", methods=["GET", "POST"])
def attendance() -> str:
    # TODO: Display based on date, slot & room_no
    return render_template("./attendance.html")


app.route("/logout")(logout)


app.errorhandler(404)(page_not_found)


if __name__ == "__main__":
    app.config.update(
        SESSION_COOKIE_SAMESITE="Strict",
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SECURE=True
    )
    app.run(host="0.0.0.0", port=5000, debug=False)
