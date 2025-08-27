from Timetable.typehints import (Connection, Cursor, FileStorage,
                                 Optional, Tuple, Dict)
from Timetable import fetch_data, show_data
from datetime import datetime
import pandas as pd


def fmt(t: str) -> datetime:
    return datetime.strptime(t, "%H:%M")


def process_slot(slot_sheet: FileStorage) -> pd.DataFrame:
    headers = ["No", "StartTime", "EndTime"]
    slots = pd.read_excel(slot_sheet, sheet_name="slots",
                          names=headers,
                          engine="openpyxl").astype({"No": "uint8"})
    return slots


def process_schedule(cursor: Cursor, /,
                     schedule_sheet: FileStorage,
                     slots: pd.DataFrame, *,
                     campus_id: Optional[int] = None) -> pd.DataFrame:
    deg_stream = {}

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
                  periods: Tuple[Dict[str, bool | int | str]]) -> None:
        start_end = {}

        def periods_intersect(start: str, end: str) -> list[int]:
            _start = fmt(start)
            _end = fmt(end)
            if period_ids := start_end.get((_start, _end)):
                return period_ids

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

    def get_students(row):
        degree, stream = row.Degree, row.Stream
        if not deg_stream.get((degree, stream)):
            programme_id = show_data.get_programme_id(cursor, degree=degree,
                                                      stream=stream)
            deg_stream[(degree, stream)] = programme_id
        return [student["reg_no"] for student in fetch_data.get_students(
            cursor, campus_id=campus_id,
            programme_id=deg_stream[(degree, stream)])]

    headers = ["Year", "Degree", "Stream", "CourseCode", "Date", "SlotNo"]
    schedules = pd.read_excel(schedule_sheet, sheet_name="schedules",
                              keep_default_na=False, parse_dates=["Date"],
                              date_format="%d/%m/%Y",
                              names=headers).astype({"Year": "int8",
                                                     "SlotNo": "int8"})
    schedules = schedules.merge(slots, how="inner", left_on="SlotNo", right_on="No")
    schedules["Sections"] = schedules.apply(get_sections, axis=1)
    schedules = schedules.explode("Sections")
    schedules = pd.concat([schedules.drop("Sections", axis=1)
                           .reset_index(drop=True),
                          pd.json_normalize(schedules["Sections"])],
                          axis=1)
    intersect(schedules, fetch_data.get_periods(cursor))
    schedules.rename(columns={"id": "SectionId", "section": "Section"},
                     inplace=True)
    schedules["Students"] = schedules.apply(get_students, axis=1)
    return schedules


def process_halls(cursor: Cursor, /,
                  hall_sheet: FileStorage,
                  schedules: pd.DataFrame, *,
                  campus_id: Optional[int] = None) -> pd.DataFrame:
    headers = ["ID", "RoomNo", "Capacity", "Columns"]
    to_types = {"ID": "uint8", "RoomNo": "unint16",
                "Capacity": "uint8", "Columns": "uint8",
                "Seat": "uint8"}
    halls = pd.read_excel(hall_sheet, sheet_name="halls",
                          names=headers,
                          engine="openpyxl")
    halls["Seat"] = 0
    halls.astype(to_types)
    return halls


def generate_hallplan(db_connector: Connection, cursor: Cursor, /, *,
                      campus_id: Optional[int] = None,
                      schedules: pd.DataFrame = pd.DataFrame(),
                      halls: pd.DataFrame = pd.DataFrame()) -> None:
    #TODO: ...
    pass
