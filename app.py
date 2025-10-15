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
from Timetable.fetch_data import get_classes
from Timetable.show_data import get_building_id, get_school_id, get_schools
from Timetable.typehints import Response
from datetime import datetime
from flask import Flask, redirect, render_template, request, url_for
from generate_hallplan import (generate_hallplan, process_hall,
                               process_schedule, process_slot, put_attendance)
from jinja2 import FileSystemLoader
import ast
import fetch_data
import os
import pandas as pd
import secrets
import string
import update_data


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
    if not sql.cursor:
        raise ValueError("Not logged in properly!")
    user, _ = sql.get_user(sql.cursor)
    return render_template("./index.html", user=user)


app.route("/about")(about)


@app.route("/upload")
def upload() -> str:
    table.clear()
    return render_template("./upload.html")


@app.route("/upload/hallplan", methods=["GET", "POST"])
def upload_hallplan() -> Response | str:
    if request.method == "GET":
        return render_template("./upload.html", action="/upload/hallplan",
                               hallplan=True)

    table.clear()
    if not sql.db_connector or not sql.cursor:
        return render_template("./failed.html",
                               reason="Not logged in properly!")

    __slots = request.files["slots"]
    process_slot(sql.db_connector, sql.cursor, __slots)
    if plan_sheet := request.files.get("plan"):
        headers = [
            "StudentID",
            "Date",
            "SlotNo",
            "CourseCode",
            "ClassID",
            "Seat"
        ]
        plan = pd.read_excel(plan_sheet, sheet_name="plan",
                             parse_dates=["Date"],
                             date_format="%d/%m/%Y",
                             names=headers,
                             engine="openpyxl")
        put_attendance(sql.db_connector, sql.cursor, plan=plan)

    else:
        return render_template("./upload.html", action="/upload/hallplan",
                               hallplan=True,
                               error_message="No plan uploaded!")
    return redirect(url_for("index"))


@app.route("/download", methods=["GET", "POST"])
def download() -> str:
    user, _ = sql.get_user(sql.cursor)
    if request.method == "GET":
        slots = fetch_data.get_slots(sql.cursor)
        slot_min = slots[0]["no"]
        slot_max = slots[-1]["no"]
        schools = tuple(school["name"] for school in get_schools(sql.cursor))
        return render_template("hall_details.html", action="/download",
                               slot_min=slot_min, slot_max=slot_max,
                               schools=schools, proceed="Download", user=user)

    if not sql.cursor:
        return render_template("./failed.html",
                               reason="Not logged in properly!")

    school = request.form["school"]
    school_id = get_school_id(sql.cursor, school=school)
    building_id = get_building_id(sql.cursor, school_id=school_id)
    slot_no = int(request.form["slot_no"])
    if room_no := request.form.get("room_no"):
        room_no = int(room_no)
    else:
        room_no = None
        _section = request.form["section"]

    date = request.form.get("date")
    if not date:
        date = datetime.today()
    else:
        date = datetime.strptime(date, "%Y-%m-%d")
    students = fetch_data.get_attendance(sql.cursor, fmt="pandas")
    cls = get_classes(sql.cursor, building_id=building_id[0], room_no=room_no)
    if not cls:
        return render_template(
            "./failed.html",
            reason=f"Invalid Room No. {room_no} for {school}"
        )
    cls_id = cls[0]["id"]
    students = fetch_data.get_attendance(sql.cursor, fmt="pandas")
    assert isinstance(students, pd.DataFrame)
    students = students.query(
        "Date.dt.date == @date.date() and ClassID == @cls_id "
        "and SlotNo == @slot_no"
    )
    if not room_no:
        year, degree, *stream, section = _section.split()
        _year = int(year)
        degree = degree.title()
        section = section.upper()
        _stream = "".join(stream) if stream else "NULL"
        students = students.query("Year == @_year and Degree == @degree "
                                  "and Stream == @_stream")

    if students.empty:
        return render_template(
            "./failed.html",
            reason=f"No Exam is going on in {school} in {room_no} "
                   f"at slot {slot_no} on {to_fmt(date)}"
        )

    students_list = students.sort_values(by="Seat").to_dict('records')
    split_index = -(-len(students_list) // 2)

    students_col1 = students_list[:split_index]
    students_col2 = students_list[split_index:]

    return render_template("print.html", date=to_fmt(date), slot_no=slot_no,
                           room_no=room_no, school=school,
                           students_col1=students_col1,
                           students_col2=students_col2)


def to_fmt(date: datetime) -> str:
    return date.strftime("%d/%m/%Y")


def _hallplan(plan: pd.DataFrame) -> None:
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

    if request.method == "GET" and not table:
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
                               dates=dates, slots=slots,
                               date=_date, slot=_slot)

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
def attendance() -> Response | str:
    if not sql.cursor:
        raise ValueError("Not logged in properly!")

    user, _ = sql.get_user(sql.cursor)
    if request.method == "GET":
        slots = fetch_data.get_slots(sql.cursor)
        slot_min = slots[0]["no"]
        slot_max = slots[-1]["no"]
        schools = tuple(school["name"] for school in get_schools(sql.cursor))
        return render_template("hall_details.html", slot_min=slot_min,
                               slot_max=slot_max, schools=schools, user=user)

    school = request.form["school"]
    school_id = get_school_id(sql.cursor, school=school)
    building_id = get_building_id(sql.cursor, school_id=school_id)
    slot_no = int(request.form["slot_no"])
    if room_no := request.form.get("room_no"):
        room_no = int(room_no)
    else:
        room_no = None
        _section = request.form["section"]

    date = request.form.get("date")
    if not date:
        date = datetime.today()
    else:
        date = datetime.strptime(date, "%Y-%m-%d")
    students = fetch_data.get_attendance(sql.cursor, fmt="pandas")
    cls = get_classes(sql.cursor, building_id=building_id[0], room_no=room_no)
    if not cls:
        return render_template(
            "./failed.html",
            reason=f"Invalid Room No. {room_no} for {school}"
        )
    cls_id = cls[0]["id"]
    students = fetch_data.get_attendance(sql.cursor, fmt="pandas")
    assert isinstance(students, pd.DataFrame)
    students = students.query(
        "Date.dt.date == @date.date() and ClassID == @cls_id "
        "and SlotNo == @slot_no"
    )
    if not room_no:
        year, degree, *stream, section = _section.split()
        year = int(year)
        degree = degree.title()
        section = section.upper()
        stream = "".join(stream) if stream else "NULL"
        students = students.query("Year == @year and Degree == @degree "
                                  "and Stream == @stream")

    if students.empty:
        return render_template(
            "./failed.html",
            reason=f"No Exam is going on in {school} in {room_no} "
                   f"at slot {slot_no} on {to_fmt(date)}"
        )
    view = True
    if request.form.get("action") == "proceed":
        view = False

    return render_template(
        "./attendance.html", view=view, date=to_fmt(date), slot_no=slot_no,
        room_no=room_no, school=school, students=students.iterrows()
    )


@app.route("/update", methods=["POST"])
def update() -> Response:
    if not sql.db_connector or not sql.cursor:
        raise ValueError("Not logged in properly!")

    date = datetime.strptime(request.form["date"], "%d/%m/%Y").date()
    slot_no = int(request.form["slot_no"])
    presentees = ast.literal_eval(request.form["presentees"])
    absentees = ast.literal_eval(request.form["absentees"])

    assert all(isinstance(presentee, int | str) for presentee in presentees)
    update_data.update_attendances(sql.db_connector, sql.cursor, [
        (True, date, slot_no, presentee)
        for presentee in presentees
    ])

    assert all(isinstance(absentee, int | str) for absentee in absentees)
    update_data.update_attendances(sql.db_connector, sql.cursor, [
        (False, date, slot_no, absentee)
        for absentee in absentees
    ])
    return redirect(url_for("index"))


@app.route("/add", methods=["GET", "POST"])
def add_user() -> Response | str:
    def add(usr: str, pwd: str) -> None | str:
        try:
            if not sql.cursor:
                raise ValueError

            sql.cursor.execute("""CREATE USER %s@'%%' IDENTIFIED BY %s""",
                               (usr, pwd))
            sql.cursor.execute("""GRANT UPDATE ON `SASTRA`.`attendance` """
                               """TO %s@'%%'""", (usr,))
            sql.cursor.execute("""GRANT SELECT ON `SASTRA`.* TO %s@'%%'""",
                               (usr,))
            sql.cursor.execute("""FLUSH PRIVILEGES""")
        except Exception:
            return render_template("./failed.html",
                                   reason="User already present")
        return None

    def generate_pwd(length: int = 12) -> str:
        alphabet = string.ascii_letters + string.digits + string.punctuation
        punctuations = set(string.punctuation)

        while True:
            pwd = "".join(secrets.choice(alphabet) for _ in range(length))
            if any(p.islower() for p in pwd) \
               and any(p.isupper() for p in pwd) \
               and any(p.isdigit() for p in pwd) \
               and any(p in punctuations for p in pwd):
                return pwd

    if sql.cursor:
        if request.method == "GET":
            return render_template("./login.html", role="Exam", user="User",
                                   auth="/add", pwd=generate_pwd())
        if (usr := request.form.get("user")) \
           and (pwd := request.form.get("password")) \
           and (failure := add(usr, pwd)):
            return failure
        return redirect(url_for("index"))
    return render_template("./failed.html",
                           reason="Not logged in properly!")


@app.route("/remove", methods=["GET", "POST"])
def remove_user() -> Response | str:
    def remove(usr: str) -> None | str:
        try:
            if sql.cursor:
                sql.cursor.execute("""DROP USER IF EXISTS %s@'%%'""", (usr,))
        except Exception:
            return render_template(
                "./failed.html", reason="Incorrect user name or access denied"
            )
        return None

    if sql.cursor:
        if request.method == "GET":
            return render_template("./login.html", role="Exam",
                                   user="User", auth="/remove",
                                   pwd_less=True, login="Remove")
        if usr := request.form.get("user"):
            if result := remove(usr):
                return result

        return redirect(url_for("index"))
    return render_template("./failed.html",
                           reason="Not logged in properly!")


app.route("/logout")(logout)


app.errorhandler(404)(page_not_found)


if __name__ == "__main__":
    app.config.update(
        SESSION_COOKIE_SAMESITE="Strict",
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SECURE=True
    )
    app.run(host="0.0.0.0", port=5000, debug=False)
