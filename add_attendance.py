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


def add_attendances(db_connector: Connection,
                    cursor: Cursor,
                    students: list[tuple[bool | int | str]]) -> None:
    cursor.executemany("""INSERT INTO `attendance`
                       (`student_id`, `date`, `slot_no`,
                       `course_code`, `class_id`, `is_present`)
                       VALUES (%s, %s, %s, %s, %s, %s)""", students)
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
