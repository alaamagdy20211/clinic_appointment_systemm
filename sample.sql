-- =================================================================
--  HealthNest Clinic – Sample Data
--  Database: PostgreSQL  |  All user passwords: Test1234!
--
--  Idempotent: safe to run multiple times on any machine.
--  No hard-coded IDs; all FK references resolved by username.
--
--  Usage:
--    PGPASSWORD='<pass>' psql -U <user> -d <dbname> -f sample.sql
-- =================================================================

BEGIN;

-- -----------------------------------------------------------------
-- 1. USERS  (no explicit id – sequence assigns it)
--    Unique key: username
--    Password hash: pbkdf2_sha256 of "Test1234!"
-- -----------------------------------------------------------------
INSERT INTO users_user
    (password, last_login, is_superuser, username,
     first_name, last_name, email, is_staff, is_active, date_joined, role)
VALUES
-- Admin
('pbkdf2_sha256$1200000$rqPfwOOJmfleJFg6ZiUQTc$6vSGPQMDm0wVmRwgU5Kbs8zPYUQmaguk01Hj8CoyM9U=',
 NULL, TRUE,  'admin_hn',
 'Ahmed',  'Hassan',  'admin@healthnest.com',         TRUE,  TRUE, NOW(), 'ADMIN'),
-- Doctors
('pbkdf2_sha256$1200000$rqPfwOOJmfleJFg6ZiUQTc$6vSGPQMDm0wVmRwgU5Kbs8zPYUQmaguk01Hj8CoyM9U=',
 NULL, FALSE, 'dr_sara_m',
 'Sara',   'Mansour', 'sara.mansour@healthnest.com',  FALSE, TRUE, NOW(), 'DOCTOR'),
('pbkdf2_sha256$1200000$rqPfwOOJmfleJFg6ZiUQTc$6vSGPQMDm0wVmRwgU5Kbs8zPYUQmaguk01Hj8CoyM9U=',
 NULL, FALSE, 'dr_karim_n',
 'Karim',  'Nour',    'karim.nour@healthnest.com',    FALSE, TRUE, NOW(), 'DOCTOR'),
('pbkdf2_sha256$1200000$rqPfwOOJmfleJFg6ZiUQTc$6vSGPQMDm0wVmRwgU5Kbs8zPYUQmaguk01Hj8CoyM9U=',
 NULL, FALSE, 'dr_layla_i',
 'Layla',  'Ibrahim', 'layla.ibrahim@healthnest.com', FALSE, TRUE, NOW(), 'DOCTOR'),
-- Receptionist
('pbkdf2_sha256$1200000$rqPfwOOJmfleJFg6ZiUQTc$6vSGPQMDm0wVmRwgU5Kbs8zPYUQmaguk01Hj8CoyM9U=',
 NULL, FALSE, 'rec_mona_f',
 'Mona',   'Farouk',  'mona.farouk@healthnest.com',  FALSE, TRUE, NOW(), 'RECEPTIONIST'),
-- Patients
('pbkdf2_sha256$1200000$rqPfwOOJmfleJFg6ZiUQTc$6vSGPQMDm0wVmRwgU5Kbs8zPYUQmaguk01Hj8CoyM9U=',
 NULL, FALSE, 'patient_ali_y',
 'Ali',    'Youssef', 'ali.youssef@example.com',      FALSE, TRUE, NOW(), 'PATIENT'),
('pbkdf2_sha256$1200000$rqPfwOOJmfleJFg6ZiUQTc$6vSGPQMDm0wVmRwgU5Kbs8zPYUQmaguk01Hj8CoyM9U=',
 NULL, FALSE, 'patient_nadia_s',
 'Nadia',  'Saleh',   'nadia.saleh@example.com',      FALSE, TRUE, NOW(), 'PATIENT'),
('pbkdf2_sha256$1200000$rqPfwOOJmfleJFg6ZiUQTc$6vSGPQMDm0wVmRwgU5Kbs8zPYUQmaguk01Hj8CoyM9U=',
 NULL, FALSE, 'patient_omar_t',
 'Omar',   'Tarek',   'omar.tarek@example.com',       FALSE, TRUE, NOW(), 'PATIENT'),
('pbkdf2_sha256$1200000$rqPfwOOJmfleJFg6ZiUQTc$6vSGPQMDm0wVmRwgU5Kbs8zPYUQmaguk01Hj8CoyM9U=',
 NULL, FALSE, 'patient_heba_m',
 'Heba',   'Mostafa', 'heba.mostafa@example.com',     FALSE, TRUE, NOW(), 'PATIENT'),
('pbkdf2_sha256$1200000$rqPfwOOJmfleJFg6ZiUQTc$6vSGPQMDm0wVmRwgU5Kbs8zPYUQmaguk01Hj8CoyM9U=',
 NULL, FALSE, 'patient_khaled_a',
 'Khaled', 'Adel',    'khaled.adel@example.com',      FALSE, TRUE, NOW(), 'PATIENT')
ON CONFLICT (username) DO NOTHING;


-- -----------------------------------------------------------------
-- 2. DOCTOR PROFILES  (no explicit id)
-- -----------------------------------------------------------------
INSERT INTO users_doctorprofile (user_id, specialization, phone_number)
SELECT u.id, v.spec, v.phone
FROM (VALUES
    ('dr_sara_m',  'Cardiology',       '+20-100-111-2222'),
    ('dr_karim_n', 'Dermatology',      '+20-100-333-4444'),
    ('dr_layla_i', 'General Practice', '+20-100-555-6666')
) AS v(uname, spec, phone)
JOIN users_user u ON u.username = v.uname
ON CONFLICT (user_id) DO NOTHING;


-- -----------------------------------------------------------------
-- 3. PATIENT PROFILES  (no explicit id)
-- -----------------------------------------------------------------
INSERT INTO users_patientprofile (user_id, phone_number)
SELECT u.id, v.phone
FROM (VALUES
    ('patient_ali_y',    '+20-101-100-0001'),
    ('patient_nadia_s',  '+20-101-100-0002'),
    ('patient_omar_t',   '+20-101-100-0003'),
    ('patient_heba_m',   '+20-101-100-0004'),
    ('patient_khaled_a', '+20-101-100-0005')
) AS v(uname, phone)
JOIN users_user u ON u.username = v.uname
ON CONFLICT (user_id) DO NOTHING;


-- -----------------------------------------------------------------
-- 4. RECEPTIONIST PROFILE  (no explicit id)
-- -----------------------------------------------------------------
INSERT INTO users_receptionistprofile (user_id, phone_number)
SELECT u.id, '+20-102-200-0001'
FROM users_user u
WHERE u.username = 'rec_mona_f'
ON CONFLICT (user_id) DO NOTHING;


-- -----------------------------------------------------------------
-- 5. DOCTOR SCHEDULES  (day_of_week: 0=Mon … 6=Sun)
--    No DB-level unique constraint: guard with WHERE NOT EXISTS.
-- -----------------------------------------------------------------
INSERT INTO scheduling_doctorschedule
    (doctor_id, day_of_week, start_time, end_time, slot_duration)
SELECT u.id, v.dow, v.st::time, v.et::time, v.dur
FROM (VALUES
    -- Dr. Sara: Mon/Wed/Thu 09:00-13:00 (30-min slots)
    ('dr_sara_m',  0, '09:00', '13:00', 30),
    ('dr_sara_m',  2, '09:00', '13:00', 30),
    ('dr_sara_m',  3, '09:00', '13:00', 30),
    -- Dr. Karim: Tue/Wed 10:00-14:00 (15-min slots)
    ('dr_karim_n', 1, '10:00', '14:00', 15),
    ('dr_karim_n', 2, '10:00', '14:00', 15),
    -- Dr. Layla: Sun/Mon 08:00-12:00 (30-min slots)
    ('dr_layla_i', 6, '08:00', '12:00', 30),
    ('dr_layla_i', 0, '08:00', '12:00', 30)
) AS v(uname, dow, st, et, dur)
JOIN users_user u ON u.username = v.uname
WHERE NOT EXISTS (
    SELECT 1 FROM scheduling_doctorschedule x
    WHERE x.doctor_id = u.id AND x.day_of_week = v.dow
);


-- -----------------------------------------------------------------
-- 6. SCHEDULE EXCEPTIONS
--    Guard with WHERE NOT EXISTS on (doctor_id, date).
-- -----------------------------------------------------------------
INSERT INTO scheduling_scheduleexception
    (doctor_id, date, start_time, end_time, slot_duration, reason, is_working_day)
SELECT
    u.id,
    v.dt::date,
    CASE WHEN v.st IS NOT NULL THEN v.st::time END,
    CASE WHEN v.et IS NOT NULL THEN v.et::time END,
    v.dur,
    v.reason,
    v.is_working
FROM (VALUES
    ('dr_sara_m',  '2026-03-11', NULL::text, NULL::text, 30,
        'Personal leave', FALSE),
    ('dr_karim_n', '2026-03-14', '10:00',    '12:00',    15,
        'Extra clinic day', TRUE),
    ('dr_layla_i', '2026-03-15', '08:00',    '10:00',    30,
        'Conference attendance – half day', TRUE)
) AS v(uname, dt, st, et, dur, reason, is_working)
JOIN users_user u ON u.username = v.uname
WHERE NOT EXISTS (
    SELECT 1 FROM scheduling_scheduleexception x
    WHERE x.doctor_id = u.id AND x.date = v.dt::date
);


-- -----------------------------------------------------------------
-- 7. APPOINTMENT SLOTS  (no explicit id)
--    Unique constraint: (doctor_id, date, start_time)
--
--    Past dates (for completed/cancelled/no-show appointments):
--      2026-02-23 Mon – Dr. Sara, Dr. Layla  (both work Mon)
--      2026-02-24 Tue – Dr. Karim            (works Tue)
--
--    Future dates (for upcoming appointments):
--      2026-03-09 Mon – Dr. Sara, Dr. Layla
--      2026-03-10 Tue – Dr. Karim
--      2026-03-11 Wed – Dr. Karim  (Sara has exception day-off)
--      2026-03-12 Thu – Dr. Sara
--      2026-03-15 Sun – Dr. Layla  (half-day exception 08:00-10:00)
-- -----------------------------------------------------------------
INSERT INTO scheduling_appointmentslot
    (doctor_id, date, start_time, end_time, is_booked, created_at)
SELECT u.id, v.dt::date, v.st::time, v.et::time, v.booked, NOW()
FROM (VALUES
    -- Dr. Sara – Mon 2026-02-23  (COMPLETED ×3, CANCELLED ×1)
    ('dr_sara_m', '2026-02-23', '09:00', '09:30', TRUE ),
    ('dr_sara_m', '2026-02-23', '09:30', '10:00', TRUE ),
    ('dr_sara_m', '2026-02-23', '10:00', '10:30', TRUE ),
    ('dr_sara_m', '2026-02-23', '10:30', '11:00', FALSE),  -- CANCELLED -> freed
    ('dr_sara_m', '2026-02-23', '11:00', '11:30', FALSE),
    ('dr_sara_m', '2026-02-23', '11:30', '12:00', FALSE),

    -- Dr. Karim – Tue 2026-02-24  (NO_SHOW ×1, COMPLETED ×1)
    ('dr_karim_n', '2026-02-24', '10:00', '10:15', FALSE),  -- NO_SHOW -> freed
    ('dr_karim_n', '2026-02-24', '10:15', '10:30', TRUE ),
    ('dr_karim_n', '2026-02-24', '10:30', '10:45', FALSE),

    -- Dr. Layla – Mon 2026-02-23  (COMPLETED ×2)
    ('dr_layla_i', '2026-02-23', '08:00', '08:30', TRUE ),
    ('dr_layla_i', '2026-02-23', '08:30', '09:00', TRUE ),
    ('dr_layla_i', '2026-02-23', '09:00', '09:30', FALSE),

    -- Dr. Sara – Mon 2026-03-09  (CHECKED_IN ×1, rest free)
    ('dr_sara_m', '2026-03-09', '09:00', '09:30', TRUE ),  -- CHECKED_IN
    ('dr_sara_m', '2026-03-09', '09:30', '10:00', FALSE),
    ('dr_sara_m', '2026-03-09', '10:00', '10:30', FALSE),
    ('dr_sara_m', '2026-03-09', '10:30', '11:00', FALSE),
    ('dr_sara_m', '2026-03-09', '11:00', '11:30', FALSE),
    ('dr_sara_m', '2026-03-09', '11:30', '12:00', FALSE),
    ('dr_sara_m', '2026-03-09', '12:00', '12:30', FALSE),
    ('dr_sara_m', '2026-03-09', '12:30', '13:00', FALSE),

    -- Dr. Sara – Thu 2026-03-12  (CONFIRMED ×1 at 09:00)
    ('dr_sara_m', '2026-03-12', '09:00', '09:30', TRUE ),
    ('dr_sara_m', '2026-03-12', '09:30', '10:00', FALSE),
    ('dr_sara_m', '2026-03-12', '10:00', '10:30', FALSE),
    ('dr_sara_m', '2026-03-12', '10:30', '11:00', FALSE),

    -- Dr. Karim – Tue 2026-03-10  (CONFIRMED ×2, REQUESTED ×1)
    ('dr_karim_n', '2026-03-10', '10:00', '10:15', TRUE ),  -- CONFIRMED
    ('dr_karim_n', '2026-03-10', '10:15', '10:30', TRUE ),  -- CONFIRMED
    ('dr_karim_n', '2026-03-10', '10:30', '10:45', TRUE ),  -- REQUESTED
    ('dr_karim_n', '2026-03-10', '10:45', '11:00', FALSE),
    ('dr_karim_n', '2026-03-10', '11:00', '11:15', FALSE),
    ('dr_karim_n', '2026-03-10', '11:15', '11:30', FALSE),
    ('dr_karim_n', '2026-03-10', '11:30', '11:45', FALSE),
    ('dr_karim_n', '2026-03-10', '11:45', '12:00', FALSE),

    -- Dr. Karim – Wed 2026-03-11  (CHECKED_IN ×1)
    ('dr_karim_n', '2026-03-11', '10:00', '10:15', TRUE ),  -- CHECKED_IN
    ('dr_karim_n', '2026-03-11', '10:15', '10:30', FALSE),
    ('dr_karim_n', '2026-03-11', '10:30', '10:45', FALSE),

    -- Dr. Layla – Mon 2026-03-09  (all free)
    ('dr_layla_i', '2026-03-09', '08:00', '08:30', FALSE),
    ('dr_layla_i', '2026-03-09', '08:30', '09:00', FALSE),
    ('dr_layla_i', '2026-03-09', '09:00', '09:30', FALSE),
    ('dr_layla_i', '2026-03-09', '09:30', '10:00', FALSE),
    ('dr_layla_i', '2026-03-09', '10:00', '10:30', FALSE),
    ('dr_layla_i', '2026-03-09', '10:30', '11:00', FALSE),

    -- Dr. Layla – Sun 2026-03-15  half-day exception (REQUESTED ×1)
    ('dr_layla_i', '2026-03-15', '08:00', '08:30', TRUE ),  -- REQUESTED
    ('dr_layla_i', '2026-03-15', '08:30', '09:00', FALSE),
    ('dr_layla_i', '2026-03-15', '09:00', '09:30', FALSE),
    ('dr_layla_i', '2026-03-15', '09:30', '10:00', FALSE)
) AS v(uname, dt, st, et, booked)
JOIN users_user u ON u.username = v.uname
ON CONFLICT (doctor_id, date, start_time) DO NOTHING;


-- -----------------------------------------------------------------
-- 8. APPOINTMENTS  (no explicit id)
--    Guard: WHERE NOT EXISTS – each slot holds at most one appt.
--    Active+completed statuses are also covered by the DB partial
--    index "unique_doctor_slot"; the WHERE NOT EXISTS is simpler
--    and handles CANCELLED / NO_SHOW too.
-- -----------------------------------------------------------------

-- COMPLETED – dr_sara_m 2026-02-23
INSERT INTO appointment_appointment
    (patient_id, doctor_id, slot_id, status, created_at, check_in_time)
SELECT pat.id, doc.id, s.id,
       'COMPLETED',
       '2026-02-20 10:00:00+02'::timestamptz,
       '2026-02-23 09:02:00+02'::timestamptz
FROM users_user pat
JOIN users_user doc ON doc.username = 'dr_sara_m'
JOIN scheduling_appointmentslot s
     ON s.doctor_id = doc.id AND s.date = '2026-02-23' AND s.start_time = '09:00'
WHERE pat.username = 'patient_ali_y'
  AND NOT EXISTS (SELECT 1 FROM appointment_appointment x WHERE x.slot_id = s.id);

INSERT INTO appointment_appointment
    (patient_id, doctor_id, slot_id, status, created_at, check_in_time)
SELECT pat.id, doc.id, s.id,
       'COMPLETED',
       '2026-02-20 10:05:00+02'::timestamptz,
       '2026-02-23 09:33:00+02'::timestamptz
FROM users_user pat
JOIN users_user doc ON doc.username = 'dr_sara_m'
JOIN scheduling_appointmentslot s
     ON s.doctor_id = doc.id AND s.date = '2026-02-23' AND s.start_time = '09:30'
WHERE pat.username = 'patient_nadia_s'
  AND NOT EXISTS (SELECT 1 FROM appointment_appointment x WHERE x.slot_id = s.id);

INSERT INTO appointment_appointment
    (patient_id, doctor_id, slot_id, status, created_at, check_in_time)
SELECT pat.id, doc.id, s.id,
       'COMPLETED',
       '2026-02-21 08:00:00+02'::timestamptz,
       '2026-02-23 10:05:00+02'::timestamptz
FROM users_user pat
JOIN users_user doc ON doc.username = 'dr_sara_m'
JOIN scheduling_appointmentslot s
     ON s.doctor_id = doc.id AND s.date = '2026-02-23' AND s.start_time = '10:00'
WHERE pat.username = 'patient_omar_t'
  AND NOT EXISTS (SELECT 1 FROM appointment_appointment x WHERE x.slot_id = s.id);

-- COMPLETED – dr_layla_i 2026-02-23
INSERT INTO appointment_appointment
    (patient_id, doctor_id, slot_id, status, created_at, check_in_time)
SELECT pat.id, doc.id, s.id,
       'COMPLETED',
       '2026-02-19 11:00:00+02'::timestamptz,
       '2026-02-23 08:03:00+02'::timestamptz
FROM users_user pat
JOIN users_user doc ON doc.username = 'dr_layla_i'
JOIN scheduling_appointmentslot s
     ON s.doctor_id = doc.id AND s.date = '2026-02-23' AND s.start_time = '08:00'
WHERE pat.username = 'patient_heba_m'
  AND NOT EXISTS (SELECT 1 FROM appointment_appointment x WHERE x.slot_id = s.id);

INSERT INTO appointment_appointment
    (patient_id, doctor_id, slot_id, status, created_at, check_in_time)
SELECT pat.id, doc.id, s.id,
       'COMPLETED',
       '2026-02-19 12:00:00+02'::timestamptz,
       '2026-02-23 08:35:00+02'::timestamptz
FROM users_user pat
JOIN users_user doc ON doc.username = 'dr_layla_i'
JOIN scheduling_appointmentslot s
     ON s.doctor_id = doc.id AND s.date = '2026-02-23' AND s.start_time = '08:30'
WHERE pat.username = 'patient_khaled_a'
  AND NOT EXISTS (SELECT 1 FROM appointment_appointment x WHERE x.slot_id = s.id);

-- COMPLETED – dr_karim_n 2026-02-24
INSERT INTO appointment_appointment
    (patient_id, doctor_id, slot_id, status, created_at, check_in_time)
SELECT pat.id, doc.id, s.id,
       'COMPLETED',
       '2026-02-22 09:00:00+02'::timestamptz,
       '2026-02-24 10:17:00+02'::timestamptz
FROM users_user pat
JOIN users_user doc ON doc.username = 'dr_karim_n'
JOIN scheduling_appointmentslot s
     ON s.doctor_id = doc.id AND s.date = '2026-02-24' AND s.start_time = '10:15'
WHERE pat.username = 'patient_ali_y'
  AND NOT EXISTS (SELECT 1 FROM appointment_appointment x WHERE x.slot_id = s.id);

-- CANCELLED – dr_sara_m 2026-02-23 10:30
INSERT INTO appointment_appointment
    (patient_id, doctor_id, slot_id, status, created_at, check_in_time)
SELECT pat.id, doc.id, s.id,
       'CANCELLED',
       '2026-02-21 14:00:00+02'::timestamptz,
       NULL
FROM users_user pat
JOIN users_user doc ON doc.username = 'dr_sara_m'
JOIN scheduling_appointmentslot s
     ON s.doctor_id = doc.id AND s.date = '2026-02-23' AND s.start_time = '10:30'
WHERE pat.username = 'patient_nadia_s'
  AND NOT EXISTS (SELECT 1 FROM appointment_appointment x WHERE x.slot_id = s.id);

-- NO_SHOW – dr_karim_n 2026-02-24 10:00
INSERT INTO appointment_appointment
    (patient_id, doctor_id, slot_id, status, created_at, check_in_time)
SELECT pat.id, doc.id, s.id,
       'NO_SHOW',
       '2026-02-22 10:00:00+02'::timestamptz,
       NULL
FROM users_user pat
JOIN users_user doc ON doc.username = 'dr_karim_n'
JOIN scheduling_appointmentslot s
     ON s.doctor_id = doc.id AND s.date = '2026-02-24' AND s.start_time = '10:00'
WHERE pat.username = 'patient_khaled_a'
  AND NOT EXISTS (SELECT 1 FROM appointment_appointment x WHERE x.slot_id = s.id);

-- CONFIRMED – dr_karim_n 2026-03-10
INSERT INTO appointment_appointment
    (patient_id, doctor_id, slot_id, status, created_at, check_in_time)
SELECT pat.id, doc.id, s.id,
       'CONFIRMED',
       NOW() - INTERVAL '3 days',
       NULL
FROM users_user pat
JOIN users_user doc ON doc.username = 'dr_karim_n'
JOIN scheduling_appointmentslot s
     ON s.doctor_id = doc.id AND s.date = '2026-03-10' AND s.start_time = '10:00'
WHERE pat.username = 'patient_ali_y'
  AND NOT EXISTS (SELECT 1 FROM appointment_appointment x WHERE x.slot_id = s.id);

INSERT INTO appointment_appointment
    (patient_id, doctor_id, slot_id, status, created_at, check_in_time)
SELECT pat.id, doc.id, s.id,
       'CONFIRMED',
       NOW() - INTERVAL '2 days',
       NULL
FROM users_user pat
JOIN users_user doc ON doc.username = 'dr_karim_n'
JOIN scheduling_appointmentslot s
     ON s.doctor_id = doc.id AND s.date = '2026-03-10' AND s.start_time = '10:15'
WHERE pat.username = 'patient_nadia_s'
  AND NOT EXISTS (SELECT 1 FROM appointment_appointment x WHERE x.slot_id = s.id);

-- CONFIRMED – dr_sara_m 2026-03-12
INSERT INTO appointment_appointment
    (patient_id, doctor_id, slot_id, status, created_at, check_in_time)
SELECT pat.id, doc.id, s.id,
       'CONFIRMED',
       NOW() - INTERVAL '5 days',
       NULL
FROM users_user pat
JOIN users_user doc ON doc.username = 'dr_sara_m'
JOIN scheduling_appointmentslot s
     ON s.doctor_id = doc.id AND s.date = '2026-03-12' AND s.start_time = '09:00'
WHERE pat.username = 'patient_omar_t'
  AND NOT EXISTS (SELECT 1 FROM appointment_appointment x WHERE x.slot_id = s.id);

-- CHECKED_IN – dr_sara_m 2026-03-09
INSERT INTO appointment_appointment
    (patient_id, doctor_id, slot_id, status, created_at, check_in_time)
SELECT pat.id, doc.id, s.id,
       'CHECKED_IN',
       NOW() - INTERVAL '2 days',
       NOW() - INTERVAL '1 hour'
FROM users_user pat
JOIN users_user doc ON doc.username = 'dr_sara_m'
JOIN scheduling_appointmentslot s
     ON s.doctor_id = doc.id AND s.date = '2026-03-09' AND s.start_time = '09:00'
WHERE pat.username = 'patient_heba_m'
  AND NOT EXISTS (SELECT 1 FROM appointment_appointment x WHERE x.slot_id = s.id);

-- CHECKED_IN – dr_karim_n 2026-03-11
INSERT INTO appointment_appointment
    (patient_id, doctor_id, slot_id, status, created_at, check_in_time)
SELECT pat.id, doc.id, s.id,
       'CHECKED_IN',
       NOW() - INTERVAL '2 days',
       NOW() - INTERVAL '30 minutes'
FROM users_user pat
JOIN users_user doc ON doc.username = 'dr_karim_n'
JOIN scheduling_appointmentslot s
     ON s.doctor_id = doc.id AND s.date = '2026-03-11' AND s.start_time = '10:00'
WHERE pat.username = 'patient_khaled_a'
  AND NOT EXISTS (SELECT 1 FROM appointment_appointment x WHERE x.slot_id = s.id);

-- REQUESTED – dr_karim_n 2026-03-10 10:30
INSERT INTO appointment_appointment
    (patient_id, doctor_id, slot_id, status, created_at, check_in_time)
SELECT pat.id, doc.id, s.id,
       'REQUESTED',
       NOW() - INTERVAL '1 day',
       NULL
FROM users_user pat
JOIN users_user doc ON doc.username = 'dr_karim_n'
JOIN scheduling_appointmentslot s
     ON s.doctor_id = doc.id AND s.date = '2026-03-10' AND s.start_time = '10:30'
WHERE pat.username = 'patient_omar_t'
  AND NOT EXISTS (SELECT 1 FROM appointment_appointment x WHERE x.slot_id = s.id);

-- REQUESTED – dr_layla_i 2026-03-15 08:00
INSERT INTO appointment_appointment
    (patient_id, doctor_id, slot_id, status, created_at, check_in_time)
SELECT pat.id, doc.id, s.id,
       'REQUESTED',
       NOW(),
       NULL
FROM users_user pat
JOIN users_user doc ON doc.username = 'dr_layla_i'
JOIN scheduling_appointmentslot s
     ON s.doctor_id = doc.id AND s.date = '2026-03-15' AND s.start_time = '08:00'
WHERE pat.username = 'patient_ali_y'
  AND NOT EXISTS (SELECT 1 FROM appointment_appointment x WHERE x.slot_id = s.id);


-- -----------------------------------------------------------------
-- 9. CONSULTATION RECORDS  (OneToOne – unique on appointment_id)
--    Only COMPLETED appointments have records.
-- -----------------------------------------------------------------
INSERT INTO appointment_consultationrecord
    (appointment_id, diagnosis, notes, created_at)
SELECT a.id, v.diag, v.notes, '2026-02-23 12:00:00+02'::timestamptz
FROM (VALUES
    ('patient_ali_y',    'dr_sara_m',  '2026-02-23', '09:00',
     'Hypertension Stage 1',
     'Prescribed lisinopril 10mg daily. Follow-up in 4 weeks. Low-sodium diet advised.'),
    ('patient_nadia_s',  'dr_sara_m',  '2026-02-23', '09:30',
     'Eczema – mild',
     'Topical hydrocortisone cream 1%, apply twice daily. Avoid harsh soaps.'),
    ('patient_omar_t',   'dr_sara_m',  '2026-02-23', '10:00',
     'Seasonal Allergic Rhinitis',
     'Loratadine 10mg once daily. Avoid known allergens.'),
    ('patient_heba_m',   'dr_layla_i', '2026-02-23', '08:00',
     'Upper respiratory tract infection',
     'Rest, fluids, paracetamol 500mg as needed. Return if fever persists > 3 days.'),
    ('patient_khaled_a', 'dr_layla_i', '2026-02-23', '08:30',
     'Routine annual check-up – all clear',
     'BMI normal. BP 120/80. Advised continued exercise.'),
    ('patient_ali_y',    'dr_karim_n', '2026-02-24', '10:15',
     'Acne vulgaris – moderate',
     'Benzoyl peroxide 5% gel, apply at night. Follow-up in 6 weeks.')
) AS v(pat_uname, doc_uname, slot_date, slot_time, diag, notes)
JOIN users_user pat ON pat.username = v.pat_uname
JOIN users_user doc ON doc.username = v.doc_uname
JOIN scheduling_appointmentslot s
     ON s.doctor_id = doc.id
    AND s.date       = v.slot_date::date
    AND s.start_time = v.slot_time::time
JOIN appointment_appointment a
     ON a.slot_id    = s.id
    AND a.patient_id = pat.id
    AND a.status     = 'COMPLETED'
ON CONFLICT (appointment_id) DO NOTHING;


-- -----------------------------------------------------------------
-- 10. RESCHEDULE LOGS
--     No DB unique constraint: guard with WHERE NOT EXISTS.
-- -----------------------------------------------------------------
-- Log 1: patient_ali_y CONFIRMED (dr_karim 2026-03-10 10:00)
--        was originally on 11:00; moved by patient
INSERT INTO appointment_appointmentreschedulelog
    (appointment_id, old_slot_id, new_slot_id, changed_by_id, reason, timestamp)
SELECT
    a.id,
    old_s.id,
    a.slot_id,
    pat.id,
    'Patient requested earlier timeslot',
    NOW() - INTERVAL '3 days'
FROM users_user pat
JOIN users_user doc    ON doc.username = 'dr_karim_n'
JOIN scheduling_appointmentslot cur_s
     ON cur_s.doctor_id = doc.id AND cur_s.date = '2026-03-10' AND cur_s.start_time = '10:00'
JOIN scheduling_appointmentslot old_s
     ON old_s.doctor_id = doc.id AND old_s.date = '2026-03-10' AND old_s.start_time = '11:00'
JOIN appointment_appointment a
     ON a.slot_id = cur_s.id AND a.patient_id = pat.id AND a.status = 'CONFIRMED'
WHERE pat.username = 'patient_ali_y'
  AND NOT EXISTS (
      SELECT 1 FROM appointment_appointmentreschedulelog x
      WHERE x.appointment_id = a.id AND x.old_slot_id = old_s.id
  );

-- Log 2: patient_nadia_s CONFIRMED (dr_karim 2026-03-10 10:15)
--        was originally on 11:15; moved by receptionist
INSERT INTO appointment_appointmentreschedulelog
    (appointment_id, old_slot_id, new_slot_id, changed_by_id, reason, timestamp)
SELECT
    a.id,
    old_s.id,
    a.slot_id,
    rec.id,
    'Doctor availability conflict – moved by receptionist',
    NOW() - INTERVAL '2 days'
FROM users_user pat
JOIN users_user doc    ON doc.username = 'dr_karim_n'
JOIN users_user rec    ON rec.username = 'rec_mona_f'
JOIN scheduling_appointmentslot cur_s
     ON cur_s.doctor_id = doc.id AND cur_s.date = '2026-03-10' AND cur_s.start_time = '10:15'
JOIN scheduling_appointmentslot old_s
     ON old_s.doctor_id = doc.id AND old_s.date = '2026-03-10' AND old_s.start_time = '11:15'
JOIN appointment_appointment a
     ON a.slot_id = cur_s.id AND a.patient_id = pat.id AND a.status = 'CONFIRMED'
WHERE pat.username = 'patient_nadia_s'
  AND NOT EXISTS (
      SELECT 1 FROM appointment_appointmentreschedulelog x
      WHERE x.appointment_id = a.id AND x.old_slot_id = old_s.id
  );


COMMIT;


-- =================================================================
--  VERIFICATION – row counts after seeding
-- =================================================================
SELECT 'users_user'                                 AS "table", COUNT(*) AS rows FROM users_user
UNION ALL SELECT 'users_doctorprofile',                 COUNT(*) FROM users_doctorprofile
UNION ALL SELECT 'users_patientprofile',                COUNT(*) FROM users_patientprofile
UNION ALL SELECT 'users_receptionistprofile',           COUNT(*) FROM users_receptionistprofile
UNION ALL SELECT 'scheduling_doctorschedule',           COUNT(*) FROM scheduling_doctorschedule
UNION ALL SELECT 'scheduling_scheduleexception',        COUNT(*) FROM scheduling_scheduleexception
UNION ALL SELECT 'scheduling_appointmentslot',          COUNT(*) FROM scheduling_appointmentslot
UNION ALL SELECT 'appointment_appointment',             COUNT(*) FROM appointment_appointment
UNION ALL SELECT 'appointment_consultationrecord',      COUNT(*) FROM appointment_consultationrecord
UNION ALL SELECT 'appointment_appointmentreschedulelog',COUNT(*) FROM appointment_appointmentreschedulelog
ORDER BY 1;


-- =================================================================
--  ANALYTICAL QUERIES WITH EXECUTION PLANS
--  Run after seeding to review costs and validate indexes.
-- =================================================================

-- -----------------------------------------------------------------
-- Q1: Appointment counts per doctor, grouped by status
--
--  Expected plan: HashAggregate over Hash Join
--  (appointment × users_user × users_doctorprofile)
--  Cost driver  : sequential scan on appointment_appointment
--  Useful index : CREATE INDEX ON appointment_appointment (doctor_id, status);
-- -----------------------------------------------------------------
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT
    u.first_name || ' ' || u.last_name AS doctor,
    dp.specialization,
    a.status,
    COUNT(*) AS total
FROM appointment_appointment a
JOIN users_user u          ON u.id = a.doctor_id
JOIN users_doctorprofile dp ON dp.user_id = u.id
GROUP BY u.id, dp.specialization, a.status
ORDER BY doctor, a.status;


-- -----------------------------------------------------------------
-- Q2: Upcoming confirmed/requested appointments for a patient
--
--  Expected plan: Bitmap Index Scan on patient_id -> Nested Loop
--  with slot (date filter) and doctor join
--  Useful index : CREATE INDEX ON appointment_appointment (patient_id, status);
-- -----------------------------------------------------------------
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT
    a.id,
    a.status,
    s.date,
    s.start_time,
    s.end_time,
    u.first_name || ' ' || u.last_name AS doctor,
    dp.specialization
FROM appointment_appointment a
JOIN scheduling_appointmentslot s  ON s.id = a.slot_id
JOIN users_user u                  ON u.id = a.doctor_id
JOIN users_doctorprofile dp        ON dp.user_id = u.id
WHERE a.patient_id = (SELECT id FROM users_user WHERE username = 'patient_ali_y')
  AND a.status IN ('REQUESTED', 'CONFIRMED')
  AND s.date >= CURRENT_DATE
ORDER BY s.date, s.start_time;


-- -----------------------------------------------------------------
-- Q3: Today's checked-in queue for a doctor
--
--  Expected plan: Index Scan on slot (doctor_id, date) ->
--  Nested Loop with appointments filtered by CHECKED_IN
--  Useful index : CREATE INDEX ON scheduling_appointmentslot (doctor_id, date);
-- -----------------------------------------------------------------
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT
    a.id,
    a.check_in_time,
    pu.first_name || ' ' || pu.last_name AS patient,
    pp.phone_number,
    s.start_time,
    s.end_time
FROM appointment_appointment a
JOIN scheduling_appointmentslot s  ON s.id = a.slot_id
JOIN users_user pu                 ON pu.id = a.patient_id
JOIN users_patientprofile pp       ON pp.user_id = pu.id
WHERE a.doctor_id = (SELECT id FROM users_user WHERE username = 'dr_sara_m')
  AND s.date      = CURRENT_DATE
  AND a.status    = 'CHECKED_IN'
ORDER BY a.check_in_time;


-- -----------------------------------------------------------------
-- Q4: Monthly appointment volume over the last 6 months
--
--  Expected plan: Seq Scan + date_trunc + Hash Aggregate by month
--  Cost driver  : full table scan when no index on created_at
--  Useful index : CREATE INDEX ON appointment_appointment (created_at);
-- -----------------------------------------------------------------
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT
    DATE_TRUNC('month', a.created_at)                              AS month,
    COUNT(*)                                                       AS total,
    COUNT(*) FILTER (WHERE a.status = 'COMPLETED')                 AS completed,
    COUNT(*) FILTER (WHERE a.status = 'CANCELLED')                 AS cancelled,
    COUNT(*) FILTER (WHERE a.status = 'NO_SHOW')                   AS no_show
FROM appointment_appointment a
WHERE a.created_at >= NOW() - INTERVAL '6 months'
GROUP BY 1
ORDER BY 1;


-- -----------------------------------------------------------------
-- Q5: Available slots per doctor for the next 7 days
--
--  Expected plan: Hash Join (slot × user × profile) with
--  bitmap index on (is_booked, date)
--  Useful index : CREATE INDEX ON scheduling_appointmentslot
--                     (doctor_id, date, is_booked);
-- -----------------------------------------------------------------
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT
    u.first_name || ' ' || u.last_name AS doctor,
    dp.specialization,
    s.date,
    COUNT(*) AS free_slots
FROM scheduling_appointmentslot s
JOIN users_user u          ON u.id = s.doctor_id
JOIN users_doctorprofile dp ON dp.user_id = u.id
WHERE s.is_booked = FALSE
  AND s.date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '7 days'
GROUP BY u.id, dp.specialization, s.date
ORDER BY s.date, doctor;


-- -----------------------------------------------------------------
-- Q6: Full reschedule audit trail for an appointment
--
--  Expected plan: FK seek on appointment_id, two slot lookups,
--  one user join
--  Useful index : CREATE INDEX ON appointment_appointmentreschedulelog
--                     (appointment_id);
-- -----------------------------------------------------------------
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT
    rl.id,
    rl.timestamp,
    cb.username                                           AS changed_by,
    os.date::text || ' ' || os.start_time::text           AS old_slot,
    ns.date::text || ' ' || ns.start_time::text           AS new_slot,
    rl.reason
FROM appointment_appointmentreschedulelog rl
JOIN users_user cb                 ON cb.id  = rl.changed_by_id
JOIN scheduling_appointmentslot os ON os.id  = rl.old_slot_id
JOIN scheduling_appointmentslot ns ON ns.id  = rl.new_slot_id
WHERE rl.appointment_id = (
    SELECT a.id
    FROM appointment_appointment a
    JOIN users_user p ON p.id = a.patient_id AND p.username = 'patient_ali_y'
    JOIN users_user d ON d.id = a.doctor_id  AND d.username = 'dr_karim_n'
    WHERE a.status = 'CONFIRMED'
    ORDER BY a.created_at DESC
    LIMIT 1
)
ORDER BY rl.timestamp;


-- -----------------------------------------------------------------
-- Q7: Doctors ranked by no-show + cancellation rate
--
--  Expected plan: HashAggregate -> HAVING + ratio compute
--  Useful index : CREATE INDEX ON appointment_appointment (doctor_id, status);
-- -----------------------------------------------------------------
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT
    u.first_name || ' ' || u.last_name  AS doctor,
    dp.specialization,
    COUNT(*)                             AS total,
    COUNT(*) FILTER (WHERE a.status IN ('NO_SHOW', 'CANCELLED')) AS bad,
    ROUND(
        100.0
        * COUNT(*) FILTER (WHERE a.status IN ('NO_SHOW', 'CANCELLED'))
        / NULLIF(COUNT(*), 0),
    1) AS bad_rate_pct
FROM appointment_appointment a
JOIN users_user u          ON u.id = a.doctor_id
JOIN users_doctorprofile dp ON dp.user_id = u.id
GROUP BY u.id, dp.specialization
HAVING COUNT(*) > 0
ORDER BY bad_rate_pct DESC NULLS LAST;


-- =================================================================
--  SUGGESTED INDEXES  (uncomment to apply; use CONCURRENTLY on
--  a live database to avoid table locks)
-- =================================================================
-- CREATE INDEX CONCURRENTLY idx_appt_doctor_status
--     ON appointment_appointment (doctor_id, status);
--
-- CREATE INDEX CONCURRENTLY idx_appt_patient_status
--     ON appointment_appointment (patient_id, status);
--
-- CREATE INDEX CONCURRENTLY idx_appt_created_at
--     ON appointment_appointment (created_at);
--
-- CREATE INDEX CONCURRENTLY idx_slot_doctor_date_booked
--     ON scheduling_appointmentslot (doctor_id, date, is_booked);
--
-- CREATE INDEX CONCURRENTLY idx_reschedule_appt
--     ON appointment_appointmentreschedulelog (appointment_id);
