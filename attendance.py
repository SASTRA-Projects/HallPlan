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


from Timetable.typehints import Connection, Cursor


def create_hallplan(db_connector: Connection, cursor: Cursor) -> None:
    r"""
    Creates tables for students' attendance and invigilators.

    Parameters
    ==========
    - **db_connector**: Connection
      The database connection object used to interact with the database.

    - **cursor**: Cursor
      A cursor object for executing SQL commands.

    Tables Created
    ==============
    - **``attendance``**: Stores attendance information for each student.
    - **``invigilator``**: Stores invigilator with date, slot number.

    Examples
    ========
    .. code-block:: python

        >>> from Timetable.mysql_connector import connect

        >>> # Create Connection object and Cursor object
        >>> connector, cursor = connect(
                user="root",
                password="secret_pwd",
                host="localhost"
            )

        >>> create_attendance(connector, cursor)

    See Also
    ========
    - `connect()` – To establish a connection with the database.
    - `create_database()` – Defines base tables before relations are added.
    - `create_relations()` – Creates relational tables for the database.
    - `create_triggers()` – To create triggers for the database.
    """
    """
    Functional Dependencies
    =======================
    - `student_id`, `date`, `slot_no` \u2192 `class_id`,
                                             `course_code`, `is_present`
    - `student_id`, `date`, `course_code` \u2192 `slot_no`
                                                 `course_code`, `is_present`
    """
    cursor.execute("""CREATE TABLE IF NOT EXISTS `attendance` (
                   `student_id` INT UNSIGNED NOT NULL,
                   `date` DATE NOT NULL,
                   `slot_no` TINYINT UNSIGNED NOT NULL,
                   `course_code` VARCHAR(10) NOT NULL,
                   `class_id` MEDIUMINT UNSIGNED NOT NULL,
                   `is_present` BOOLEAN NOT NULL,
                   PRIMARY KEY(`date`, `slot_no`, `student_id`),
                   FOREIGN KEY(`student_id`) REFERENCES `students`(`id`)
                   ON UPDATE CASCADE ON DELETE RESTRICT,
                   FOREIGN KEY(`class_id`) REFERENCES `classes`(`id`)
                   ON UPDATE CASCADE ON DELETE RESTRICT
    )""")
    """
    Functional Dependencies
    =======================
    - `faculty_id`, `date`, `slot_no` \u2192 `class_id`
    - `class_id`, `date` \u2192 `faculty_id`
    """
    cursor.execute("""CREATE TABLE IF NOT EXISTS `invigilators` (
                   `faculty_id` MEDIUMINT UNSIGNED NOT NULL,
                   `date` DATE NOT NULL,
                   `slot_no` TINYINT UNSIGNED NOT NULL,
                   `class_id` MEDIUMINT UNSIGNED NOT NULL,
                   PRIMARY KEY(`date`, `slot_no`, `faculty_id`),
                   FOREIGN KEY(`faculty_id`) REFERENCES `faculties`(`id`)
                   ON UPDATE CASCADE ON DELETE RESTRICT,
                   FOREIGN KEY(`class_id`) REFERENCES `classes`(`id`)
                   ON UPDATE CASCADE ON DELETE RESTRICT,
                   UNIQUE(`date`, `class_id`, `faculty_id`),
                   FOREIGN KEY(`date`, `slot_no`)
                   REFERENCES `attendance`(`date`, `slot_no`)
                   ON UPDATE CASCADE ON DELETE RESTRICT
    )""")
