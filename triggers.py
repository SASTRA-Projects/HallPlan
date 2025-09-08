from Timetable.typehints import Connection, Cursor


def create_triggers(db_connector: Connection, cursor: Cursor):
    cursor.execute("""SET GLOBAL event_scheduler = ON""")
    cursor.execute("""CREATE TRIGGER IF NOT EXISTS `grant_faculty_update`
                   AFTER INSERT ON `invigilators`
                   FOR EACH ROW
                   BEGIN
                    DECLARE slot_start TIME;
                    DECLARE slot_end TIME;
                    DECLARE current_time TIME;

                    SET current_time = CURTIME();

                    SELECT `start_time`, `end_time`
                    INTO slot_start, slot_end
                    FROM `slots`
                    WHERE `slot_no` = NEW.`slot_no`;

                    IF current_time >= slot_start AND current_time < slot_end
                    THEN SET @sql = CONCAT('GRANT UPDATE ON `SASTRA`.`attendance` TO ''', NEW.`faculty_id`, '''@''%''');
                        PREPARE stmt FROM @sql;
                        EXECUTE stmt;
                        DEALLOCATE PREPARE stmt;
                    END IF;
                   END;
    """)
    cursor.execute("""CREATE EVENT IF NOT EXISTS `revoke_old_privileges_event`
                   ON SCHEDULE EVERY 1 DAY
                   STARTS (CURDATE() + INTERVAL 1 DAY)
                   ON COMPLETION PRESERVE
                   DO
                   BEGIN
                    DECLARE done INT DEFAULT FALSE;
                    DECLARE faculty_id MEDIUMINT UNSIGNED;
                    DECLARE slot_no TINYINT UNSIGNED;
                    DECLARE invigilator_cursor CURSOR FOR
                        SELECT `faculty_id`, `slot_no`
                        FROM `invigilators` `I`
                        JOIN `slots` `S` ON `I`.`slot_no` = `S`.`slot_no`
                        WHERE `I`.`date` = CURDATE() AND CURTIME() >= `S`.`end_time`;
                    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

                    OPEN invigilator_cursor;

                    read_loop: LOOP
                        FETCH invigilator_cursor INTO faculty_id, slot_no;
                        IF done THEN
                            LEAVE read_loop;
                        END IF;

                        SET @sql = CONCAT('REVOKE UPDATE ON `SASTRA`.`attendance` FROM ''', faculty_id, '''@''%''');
                        PREPARE stmt FROM @sql;
                        EXECUTE stmt;
                        DEALLOCATE PREPARE stmt;

                        DELETE FROM `invigilators`
                        WHERE `faculty_id`=faculty_id AND `slot_no` = slot_no AND `date` = CURDATE();
                    END LOOP;

                    CLOSE invigilator_cursor;
                   END;
    """)
