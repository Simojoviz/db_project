-- User prenotation with user fullname, shift info and course and trainers name
SELECT u.fullname, s.date, s.h_start, s.h_end, s.room_id, co.name, u2.fullname as Trainer
FROM prenotations pr
JOIN users u ON pr.client_id = u.id
JOIN shifts s ON pr.shift_id = s.id
JOIN courses co ON s.course_id = co.id
JOIN users u2 ON co.instructor_id = u2.id

-- Users and their Roles
SELECT u.fullname, r.name
FROM users u JOIN user_roles ur ON u.id = ur.user_id
JOIN roles r ON r.id = ur.role_id

-- Messages
SELECT u1.fullname AS sender, m.text AS text, u2.fullname AS reciever
FROM users u1 JOIN messages m ON u1.id = m.sender
	 JOIN users u2 ON m.addressee = u2.id

-- Courses
SELECT u.fullname AS name, c.name AS course_name, u2.fullname AS trainer
FROM users u JOIN course_signs_up csu ON u.id = csu.user_id
	JOIN courses c ON csu.course_id = c.id
	JOIN users u2 ON c.instructor_id = u2.id

-- User remaining Prenotations --
-- in prenotations page --
SELECT s.date, s.starting, s.ending, r.name AS room_name
FROM users u JOIN prenotations p ON u.id = p.user_id 
		     JOIN shifts s ON  s.id = p.shift_id
		     JOIN rooms r ON s.room_id = r.id
WHERE u.fullname = 'Name Surname' AND ((s.date = 'YYYY-MM-DD' AND s.ending >= 'hh:mm:ss') OR s.date > 'YYYY-MM-DD')
-- current date and current time

-- User Current Courses sign ups --
SELECT c.name, c.starting, c.ending
FROM users u JOIN course_signs_up cs ON u.id = cs.user_id
				JOIN courses c ON c.id = cs.course_id
WHERE u.fullname = 'Name Surname' AND c.ending >= 'YYYY-MM-DD'

-- Course shifts --
SELECT s.date, s.starting, s.ending, r.name as room_name
FROM courses c JOIN shifts s ON c.id = s.course_id 
				JOIN rooms r ON r.id = s.room_id
WHERE c.name = 'Course Name' AND s.date >= 'YYYY-MM-DD'

-- Course users --
SELECT u.fullname
FROM users u JOIN course_signs_up cs ON u.id = cs.user_id 
			 JOIN courses c ON c.id = cs.course_id
WHERE c.name='Course Name'

-- Shift users --
SELECT u.fullname
FROM shifts s JOIN prenotations p ON s.id = p.shift_id
			  JOIN users u ON u.id = p.user_id
WHERE s.date = 'YYYY-MM-DD' AND s.starting = 'hh:mm:ss'