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


from Timetable.typehints import Cursor, Literal, Optional
import datetime
import pandas as pd

"""
Shows the data for tables,
for which data will change frequently.
"""


def get_attendance(
    cursor: Cursor, /, *,
    fmt: Literal["sql", "pandas"] = "sql",
    date: Optional[datetime.date] = None,
    slot_no: Optional[int] = None,
    section_id: Optional[int] = None,
    class_id: Optional[int] = None,
    course_code: Optional[str] = None,
    student_id: Optional[int] = None,
    is_present: Optional[bool] = None
) -> pd.DataFrame | tuple[dict[str, int | str | bool], ...]:
    if fmt == "pandas":
        cursor.execute("""SELECT `date` AS `Date`,
                       `slot_no` AS `SlotNo`,
                       `degree` AS `Degree`,
                       `stream` AS `Stream`,
                       `year` AS `Year`,
                       `section` AS `Section`,
                       `room_no` AS `RoomNo`,
                       `course_code` AS `CourseCode`,
                       CONCAT(
                            `campus_id`,
                            LPAD(MOD((`join_year` + `duration`),
                                 100), 2, '0'),
                            LPAD(`programme_id`, 3, '0'),
                            LPAD(`roll_no`, 3, '0')
                       ) AS `RegNo`
                       FROM `attendance` `att`
                       JOIN `classes`
                       ON `class_id`=`classes`.`id`
                       JOIN `section_student_details` `SSD`
                       ON `att`.`student_id`=`SSD`.`student_id`
                       JOIN `degrees`
                       ON `degrees`.`name`=`degree`""")
        return pd.DataFrame(cursor.fetchall(), copy=False)

    if date:
        if slot_no:
            if section_id:
                cursor.execute("""SELECT `course_code`, `class_id`
                               `student_id`, `is_present`
                               FROM `attendance` `att`
                               JOIN `section_students` `SS`
                               ON `att`.`student_id`=`SS`.`student_id`
                               AND `date`=%s,
                               AND `slot_no`=%s
                               AND `SS`.`section_id`=%s""",
                               (date, slot_no, section_id))
            else:
                cursor.execute("""SELECT `course_code`, `class_id`
                               `student_id`, `is_present`
                               FROM `attendance`
                               WHERE `date`=%s,
                               AND `slot_no`=%s""", (date, slot_no))
        elif section_id:
            cursor.execute("""SELECT `course_code`, `slot_no`
                           `class_id`, `student_id`, `is_present`
                           FROM `attendance` `att`
                           JOIN `section_students` `SS`
                           ON `att`.`student_id`=`SS`.`student_id`
                           AND `date`=%s,
                           AND `SS`.`section_id`=%s""",
                           (date, section_id))
    elif slot_no:
        if section_id:
            cursor.execute("""SELECT `date`, `course_code`, `class_id`
                           `student_id`, `is_present`
                           FROM `attendance` `att`
                           JOIN `section_students` `SS`
                           ON `att`.`student_id`=`SS`.`student_id`
                           AND `slot_no`=%s
                           AND `SS`.`section_id`=%s""",
                           (slot_no, section_id))
        else:
            cursor.execute("""SELECT `date`, `course_code`,
                           `class_id`, `student_id`, `is_present`
                           FROM `attendance`
                           WHERE `slot_no`=%s""", (slot_no,))
    elif section_id:
        cursor.execute("""SELECT `date`, `slot_no`, `course_code`,
                       `class_id`, `course_code`,
                       `student_id`, `is_present`
                       FROM `attendance` `att`
                       JOIN `section_students` `SS`
                       ON `att`.`student_id`=`SS`.`student_id`
                       AND `SS`.`section_id`=%s""", (section_id,))
    else:
        cursor.execute("""SELECT * FROM `attendance`""")

    res = cursor.fetchall()
    if course_code:
        res = tuple(d for d in res if d.pop("course_code") == course_code)
    if class_id:
        res = tuple(d for d in res if d.pop("class_id") == class_id)
    if student_id:
        res = tuple(d for d in res if d.pop("student_id") == student_id)
    if is_present is not None:
        res = tuple(d for d in res if d.pop("is_present") == is_present)
    return res


def get_invigilator(
    cursor: Cursor, /, *,
    date: Optional[datetime.date] = None,
    slot_no: Optional[int] = None,
    section_id: Optional[int] = None,
    course_code: Optional[str] = None,
    faculty_id: Optional[int] = None
) -> tuple[dict[str, int | str], ...]:
    if date:
        if slot_no:
            if section_id:
                cursor.execute("""SELECT `faculty_id`, `class_id`
                               FROM `invigilators` `inv`
                               JOIN `attendance` `att`
                               ON `att`.`date`=`inv`.`date`
                               AND `att`.`slot_no`=`inv`.`slot_no`
                               AND `att`.`date`=%s
                               AND `att`.`slot_no`=%s
                               JOIN `section_students` `SS`
                               ON `SS`.`student_id`=`att`.`student_id`
                               AND `att`.`section_id`=%s""",
                               (date, slot_no, section_id))
            else:
                cursor.execute("""SELECT `faculty_id`, `class_id`
                               FROM `invigilators` `inv`
                               JOIN `attendance` `att`
                               ON `att`.`date`=`inv`.`date`
                               AND `att`.`slot_no`=`inv`.`slot_no`
                               AND `att`.`date`=%s
                               AND `att`.`slot_no`=%s""",
                               (date, slot_no))
        elif section_id:
            cursor.execute("""SELECT `faculty_id`, `slot_no`, `class_id`
                           FROM `invigilators` `inv`
                           JOIN `attendance` `att`
                           ON `att`.`date`=`inv`.`date`
                           AND `att`.`slot_no`=`inv`.`slot_no`
                           AND `att`.`date`=%s
                           JOIN `section_students` `SS`
                           ON `SS`.`student_id`=`att`.`student_id`
                           AND `att`.`section_id`=%s""",
                           (slot_no, section_id))
        else:
            cursor.execute("""SELECT `faculty_id`, `slot_no`, `class_id`
                           FROM `invigilators` `inv`
                           JOIN `attendance` `att`
                           ON `att`.`date`=`inv`.`date`
                           AND `att`.`date`=%s
                           AND `att`.`slot_no`=`inv`.`slot_no`""",
                           (date,))
    elif slot_no:
        if section_id:
            cursor.execute("""SELECT `faculty_id`, `date`, `class_id`
                           FROM `invigilators` `inv`
                           JOIN `attendance` `att`
                           ON `att`.`date`=`inv`.`date`
                           AND `att`.`slot_no`=`inv`.`slot_no`
                           AND `att`.`date`=%s
                           JOIN `section_students` `SS`
                           ON `SS`.`student_id`=`att`.`student_id`
                           AND `att`.`section_id`=%s""",
                           (slot_no, section_id))
        else:
            cursor.execute("""SELECT `faculty_id`, `date`, `class_id`
                           FROM `invigilator` `inv`
                           JOIN `attendance` `att`
                           ON `att`.`date`=`inv`.`date`
                           AND `att`.`slot_no`=`inv`.`slot_no`
                           AND `att`.`slot_no`=%s""", (slot_no,))
    elif section_id:
        cursor.execute("""SELECT `faculty_id`, `date`,
                       `slot_no`, `class_id`
                       FROM `invigilators` `inv`
                       JOIN `attendance` `att`
                       ON `att`.`date`=`inv`.`date`
                       AND `att`.`slot_no`=`inv`.`slot_no`
                       JOIN `section_students` `SS`
                       ON `SS`.`student_id`=`att`.`student_id`
                       AND `att`.`section_id`=%s""", (section_id,))
    else:
        cursor.execute("""SELECT * FROM `invigilators`""")

    res = cursor.fetchall()
    if faculty_id:
        res = tuple(d for d in res if d.pop("faculty_id") == faculty_id)

    return res
