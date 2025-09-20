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
Updates the attendance and invigilator tables.
"""


def update_attendance(db_connector: Connection,
                      cursor: Cursor, /, *,
                      student_id: Optional[int],
                      date: Optional[datetime.date],
                      slot_no: Optional[int],
                      is_present: Optional[bool]) -> None:
    cursor.execute("""UPDATE `attendance`
                   SET `is_present`=%s
                   WHERE `date`=%s
                   AND `slot_no`=%s
                   AND `student_id`=%s""",
                   (is_present, date, slot_no, student_id))
    db_connector.commit()


def update_attendances(db_connector: Connection,
                       cursor: Cursor,
                       students: list[tuple[bool | int | str]]) -> None:
    cursor.executemany("""UPDATE `attendance`
                       SET `is_present`=%s
                       WHERE `date`=%s
                       AND `slot_no`=%s
                       AND `student_id`=%s""", students)
    db_connector.commit()


def update_invigilator(db_connector: Connection,
                       cursor: Cursor, /, *,
                       faculty_id: Optional[int] = None,
                       date: Optional[datetime.date] = None,
                       slot_no: Optional[int] = None,
                       class_id: Optional[int] = None) -> None:
    cursor.execute("""UPDATE `invigilator`
                   SET `faculty_id`=%s
                   WHERE `date`=%s
                   AND `slot_no`=%s
                   AND `class_id`=%s""",
                   (faculty_id, date, slot_no, class_id))
    db_connector.commit()
