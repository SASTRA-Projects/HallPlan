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


from Timetable.typehints import Connection, Cursor, FileStorage, Optional
from Timetable import fetch_data, show_data
from datetime import datetime
from random import randint
import add_attendance as add_att
import attendance
import pandas as pd
import pymysql


def fmt(t: str) -> datetime:
    return datetime.strptime(t, "%H:%M")


def process_slot(db_connector: Connection, cursor: Cursor, /,
                 slot_sheet: FileStorage) -> pd.DataFrame:
    attendance.create_hallplan(db_connector, cursor)
    headers = ["No", "StartTime", "EndTime"]
    slots = pd.read_excel(slot_sheet, sheet_name="slots",
                          names=headers,
                          engine="openpyxl").astype({"No": "uint8"},
                                                    copy=False)
    try:
        for _, slot in slots.iterrows():
            add_att.add_slot(db_connector, cursor,
                             no=slot.No,
                             start_time=slot.StartTime,
                             end_time=slot.EndTime)
    except pymysql.err.IntegrityError as exception:
        print(exception)

    return slots


def process_schedule(cursor: Cursor, /,
                     schedule_sheet: FileStorage,
                     slots: pd.DataFrame, *,
                     campus_id: Optional[int] = None) -> pd.DataFrame:
    deg_stream: dict[tuple[str, str], int] = {}

    def get_sections(row: pd.Series) -> list[dict[str, int | str]]:
        year, degree, stream = row[["Year", "Degree", "Stream"]]
        return [sections
                for sections in fetch_data.get_sections(
                    cursor,
                    campus_id=campus_id,
                    degree=degree,
                    stream=stream,
                    year=year)]

    def intersect(schedules: pd.DataFrame,
                  periods: tuple[dict[str, bool | int | str]]) -> None:
        start_end: dict[tuple[datetime, datetime], int] = {}

        def periods_intersect(start: str, end: str) -> list[int]:
            _start = fmt(start)
            _end = fmt(end)
            if period_ids := start_end.get((_start, _end)):
                return [period_ids]

            _pstart = _pend = 0
            for period in periods:
                pstart = fmt(period["start_time"])
                pend = fmt(period["end_time"])
                if pstart <= _start:
                    _pstart = period["id"]
                elif _end <= pend:
                    _pend = period["id"]
                    break

            start_end[(start, end)] = set(range(_pstart, _pend + 1))
            return start_end[(start, end)]

        schedules["Periods"] = schedules.apply(
            lambda row: periods_intersect(row.StartTime, row.EndTime),
            axis=1
        )

    def get_students(section):
        degree, stream = section.Degree, section.Stream
        stream = stream if stream else "NULL"
        if not deg_stream.get((degree, stream)):
            programme_id = show_data.get_programme_id(cursor, degree=degree,
                                                      stream=stream)
            deg_stream[(degree, stream)] = programme_id

        return [(std["reg_no"], std["id"]) for std in fetch_data.get_students(
            cursor, campus_id=campus_id,
            programme_id=deg_stream[(degree, stream)],
            section_id=section.SectionID)]

    headers = ["Year", "Degree", "Stream", "CourseCode", "Date", "SlotNo"]
    schedules = pd.read_excel(
        schedule_sheet, sheet_name="schedules",
        keep_default_na=False, parse_dates=["Date"],
        date_format="%d/%m/%Y",
        names=headers
    ).astype({"Year": "uint8", "SlotNo": "category"}, copy=False)
    schedules = schedules.merge(slots, how="inner",
                                left_on="SlotNo", right_on="No")
    schedules["Sections"] = schedules.apply(get_sections, axis=1)
    schedules = schedules.explode("Sections")
    schedules = pd.concat([schedules.drop("Sections", axis=1)
                           .reset_index(drop=True),
                          pd.json_normalize(schedules["Sections"])],
                          axis=1)
    intersect(schedules, fetch_data.get_periods(cursor))
    schedules.rename(columns={"id": "SectionID", "section": "Section"},
                     inplace=True)
    schedules["Students"] = schedules.apply(get_students, axis=1)
    return schedules


def process_hall(cursor: Cursor, /,
                 hall_sheet: FileStorage,
                 building_id: Optional[int] = None) -> pd.DataFrame:
    def get_class(room_no):
        cls = fetch_data.get_class(cursor, building_id=building_id,
                                   room_no=room_no)
        return cls["id"] if cls else None

    headers = ["RoomNo", "Capacity", "Date", "SlotNo"]
    to_types = {"ID": "uint16", "RoomNo": "uint16",
                "Capacity": "uint8", "Seat": "uint8"}
    halls = pd.read_excel(hall_sheet, sheet_name="halls",
                          parse_dates=["Date"],
                          date_format="%d/%m/%Y",
                          names=headers,
                          engine="openpyxl")
    halls["ID"] = halls.apply(
        lambda hall: get_class(hall.RoomNo),
        axis=1
    )
    halls["Seat"] = 0
    halls = halls.astype(to_types, copy=False)
    return halls


def put_attendance(
    db_connector: Connection,
    cursor: Cursor,
    plan: pd.DataFrame
) -> None:
    students = []
    for _, data in plan.iterrows():
        students.append((
            data.StudentID,
            data.Date,
            data.SlotNo,
            data.CourseCode,
            data.ClassID,
            data.Seat,
            True
        ))
    add_att.add_attendances(db_connector, cursor, students)


def generate_hallplan(db_connector: Connection, cursor: Cursor, /, *,
                      schedules: pd.DataFrame = pd.DataFrame(),
                      halls: pd.DataFrame = pd.DataFrame()) -> pd.DataFrame:
    plan = pd.DataFrame(columns=["Date", "SlotNo", "Degree", "Stream", "Year",
                                 "Section", "ClassID", "RoomNo", "CourseCode",
                                 "Seat", "RegNo", "StudentID"])
    to_types = {
        "SlotNo": "uint8",
        "Year": "uint16",
        "ClassID": "uint32",
        "Seat": "uint8",
        "StudentID": "uint32"
    }
    for ds, grouped in schedules.groupby(["Date", "SlotNo"]):
        prg_years = []
        _halls = halls.query("Date == @ds[0] and SlotNo == @ds[1]")
        n = len(_halls)
        hall_idx = randint(0, n-1)
        for _, row in grouped.sort_values(by=["CourseCode"]).iterrows():
            prg_year = [row["Degree"], row["Stream"], row["Year"]]
            if prg_year not in prg_years:
                prg_years.append(prg_year)
        for prg_year in prg_years:
            d, s, y = prg_year
            prg_yr_schedule = grouped.query("Degree == @d and Stream == @s "
                                            "and Year == @y")
            for _, section in prg_yr_schedule.iterrows():
                students = section.Students
                course_code = section.CourseCode
                no_of_students = len(students)
                while no_of_students:
                    hall = _halls.iloc[hall_idx]
                    cap = hall.Capacity
                    half = cap // 2
                    occupy = min(no_of_students, abs(half - hall.Seat))

                    assert cap, "Insufficient no. of seats!"
                    for i in range(occupy):
                        plan = pd.concat([plan, pd.DataFrame([[
                                *ds, *prg_year, section.Section,
                                hall.ID, hall.RoomNo, course_code,
                                hall.Seat + i + 1, *students[i]
                            ]], columns=plan.columns)],
                            axis=0, ignore_index=True)
                    students = students[occupy:]
                    no_of_students = len(students)
                    seat = hall.Seat + occupy

                    _halls.at[hall_idx, "Capacity"] = cap - seat
                    _halls.at[hall_idx, "Seat"] = seat
                    if seat in (half, cap):
                        hall_idx = (hall_idx + 1) % n

    plan["Date"] = pd.to_datetime(plan["Date"], format="%d/%m/%Y")
    plan = plan.astype(to_types, copy=False)
    try:
        put_attendance(db_connector, cursor, plan)
    except pymysql.err.IntegrityError as exception:
        print(exception)
        raise

    return plan
