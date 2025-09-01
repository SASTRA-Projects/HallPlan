from Timetable.typehints import Cursor, Optional
import datetime

"""
Shows the data for tables,
for which data will change frequently.
"""


def get_attendance(
    cursor: Cursor, /, *,
    date: Optional[datetime.date] = None,
    slot_no: Optional[int] = None,
    section_id: Optional[int] = None,
    class_id: Optional[int] = None,
    course_code: Optional[str] = None,
    student_id: Optional[int] = None,
    is_present: Optional[bool] = None
) -> tuple[dict[str, int | str | bool], ...]:
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
