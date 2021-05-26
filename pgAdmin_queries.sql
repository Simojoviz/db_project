-- User prenotation with user fullname, shift info and course and trainers name
SELECT u.fullname, s.date, s.h_start, s.h_end, co.name, u2.fullname as Trainer
FROM prenotations pr
JOIN users u ON pr.client_id = u.id
JOIN shifts s ON pr.shift_id = s.id
JOIN courses co ON s.course_id = co.id
JOIN users u2 ON co.instructor_id = u2.id
