from Timetable.typehints import Connection, Cursor, Optional
import datetime

"""
Adds the data to the attendance and invigilator tables.
"""


def add_attendance(db_connector: Connection,
                   cursor: Cursor, /, *,
                   student_id: Optional[int] = None,
                   date: Optional[datetime.date] = None,
                   slot_no: Optional[int] = None,
                   course_code: Optional[str] = None,
                   class_id: Optional[int] = None,
                   is_present: Optional[bool]) -> None:
    cursor.execute("""INSERT INTO `attendance`
                   (`student_id`, `date`, `slot_no`,
                   `course_code`, `class_id`, `is_present`)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                   (student_id, date, slot_no,
                    course_code, class_id, is_present))
    db_connector.commit()


def add_invigilator(db_connector: Connection,
                    cursor: Cursor, /, *,
                    faculty_id: Optional[int] = None,
                    date: Optional[datetime.date] = None,
                    slot_no: Optional[int] = None,
                    class_id: Optional[int] = None) -> None:
    cursor.execute("""INSERT INTO `invigilator`
                   (`faculty_id`, `date`, `slot_no`, `class_id`)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                   (faculty_id, date, slot_no, class_id))
    db_connector.commit()
