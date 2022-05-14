DELETE FROM user_type;
DELETE FROM sqlite_sequence WHERE name = 'user_type';

INSERT INTO user_type(user_type, allow_edit) VALUES('teacher', TRUE);
INSERT INTO user_type(user_type, allow_edit) VALUES('student', FALSE);


