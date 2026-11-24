-- data.sql : sample data for the wordtest database (HW3)
-- Run AFTER schema.sql.  All sample accounts use the password: password123
-- (stored as plain text)

use wordtest;
set names utf8mb4;

-- 1. Teacher ---------------------------------------------------------------
insert into Teacher (TeacherID, FirstName, LastName, Email, Password) values
(1, 'Minjun', 'Kim',  'minjun.kim@school.kr',  'password123'),
(2, 'Seoyeon', 'Lee', 'seoyeon.lee@school.kr', 'password123'),
(3, 'Jihoon', 'Park',  'jihoon.park@school.kr', 'password123'),
(4, 'Haeun', 'Choi',   'haeun.choi@school.kr',  'password123'),
(5, 'Doyun', 'Jung',   'doyun.jung@school.kr',  'password123');

-- 2. TeacherPhoneNumber ------------------------------------------------------
insert into TeacherPhoneNumber (TeacherID, PhoneNumber) values
(1, '010-1111-2222'),
(1, '043-260-1001'),
(2, '010-2222-3333'),
(3, '010-3333-4444'),
(4, '010-4444-5555'),
(5, '010-5555-6666');

-- 3. Student -----------------------------------------------------------------
insert into Student (StudentID, FirstName, LastName, Email, Password) values
(101, 'Yuna',   'Han',  'yuna.han@student.kr',   'password123'),
(102, 'Junseo', 'Yoon', 'junseo.yoon@student.kr', 'password123'),
(103, 'Soyul',  'Kang', 'soyul.kang@student.kr',  'password123'),
(104, 'Taemin', 'Shin', 'taemin.shin@student.kr', 'password123'),
(105, 'Areum',  'Song', 'areum.song@student.kr',  'password123'),
(106, 'Hyunwoo','Jang', 'hyunwoo.jang@student.kr','password123');

-- 4. StudentPhoneNumber ------------------------------------------------------
insert into StudentPhoneNumber (StudentID, PhoneNumber) values
(101, '010-7000-0101'),
(102, '010-7000-0102'),
(103, '010-7000-0103'),
(104, '010-7000-0104'),
(105, '010-7000-0105'),
(106, '010-7000-0106'),
(106, '010-8000-0106');

-- 5. WordFile ----------------------------------------------------------------
insert into WordFile (FileID, FileName, UploadDate, TeacherID) values
(1, 'TOEIC Basic Vocabulary', '2026-09-01', 1),
(2, 'Middle School Day 1',    '2026-09-03', 1),
(3, 'CSAT Core Words',        '2026-09-10', 2),
(4, 'Business English',       '2026-09-15', 3),
(5, 'Travel English',         '2026-09-20', 4);

-- 6. Word --------------------------------------------------------------------
insert into Word (FileID, WordNumber, WordContent, Meaning) values
(1, 1, 'abandon',      '버리다, 포기하다'),
(1, 2, 'allocate',     '할당하다, 배분하다'),
(1, 3, 'comply',       '따르다, 준수하다'),
(1, 4, 'deadline',     '마감 기한'),
(1, 5, 'negotiate',    '협상하다'),
(2, 1, 'apple',        '사과'),
(2, 2, 'borrow',       '빌리다'),
(2, 3, 'curious',      '호기심 많은'),
(2, 4, 'delicious',    '맛있는'),
(2, 5, 'environment',  '환경'),
(3, 1, 'abundant',     '풍부한'),
(3, 2, 'inevitable',   '불가피한'),
(3, 3, 'reluctant',    '꺼리는, 마지못한'),
(3, 4, 'sustain',      '지속하다, 유지하다'),
(3, 5, 'hypothesis',   '가설'),
(4, 1, 'invoice',      '송장, 청구서'),
(4, 2, 'revenue',      '수익, 매출'),
(4, 3, 'stakeholder',  '이해관계자'),
(4, 4, 'merger',       '합병'),
(4, 5, 'quarterly',    '분기별의'),
(5, 1, 'itinerary',    '여행 일정'),
(5, 2, 'luggage',      '짐, 수하물'),
(5, 3, 'reservation',  '예약'),
(5, 4, 'customs',      '세관'),
(5, 5, 'souvenir',     '기념품');

-- 7. IncorrectWord -----------------------------------------------------------
insert into IncorrectWord (IncorrectWordID, WrongCount, RegisterDate, FileID, WordNumber, StudentID) values
(1, 3, '2026-10-03', 1, 1, 101),
(2, 1, '2026-10-03', 1, 2, 101),
(3, 2, '2026-10-04', 1, 3, 102),
(4, 4, '2026-10-04', 2, 1, 102),
(5, 1, '2026-10-06', 3, 2, 103),
(6, 2, '2026-10-06', 3, 4, 103),
(7, 1, '2026-10-07', 4, 1, 104),
(8, 5, '2026-10-07', 1, 1, 105);

-- 8. IncorrectWordGroup ------------------------------------------------------
-- auto groups must have a FileID (CH_IncorrectWordGroup_GroupType_FileID)
insert into IncorrectWordGroup (GroupID, GroupName, GroupType, CreateDate, FileID, StudentID) values
(1, 'TOEIC Wrong Words',  'auto',   '2026-10-05', 1,    101),
(2, 'Review List',        'manual', '2026-10-08', null, 101),
(3, 'TOEIC Mistakes',     'auto',   '2026-10-10', 1,    102),
(4, 'My Hard Words',      'manual', '2026-10-12', null, 103),
(5, 'CSAT Wrong Words',   'auto',   '2026-10-15', 3,    103);

-- 9. Test --------------------------------------------------------------------
-- normal -> GroupID null, wrong -> GroupID required (CH_Test_TestType_GroupID)
insert into Test (TestID, TestType, TestDate, StudentID, GroupID) values
(1, 'normal', '2026-10-03', 101, null),
(2, 'wrong',  '2026-10-09', 101, 1),
(3, 'normal', '2026-10-04', 102, null),
(4, 'wrong',  '2026-10-11', 102, 3),
(5, 'normal', '2026-10-06', 103, null),
(6, 'normal', '2026-10-07', 104, null),
(7, 'wrong',  '2026-10-16', 103, 5);

-- 10. TestResult (CorrectCount + IncorrectCount = QuestionCount) -------------
insert into TestResult (ResultID, QuestionCount, CorrectCount, IncorrectCount, TestID) values
(1, 5, 3, 2, 1),
(2, 2, 1, 1, 2),
(3, 5, 4, 1, 3),
(4, 1, 0, 1, 4),
(5, 5, 5, 0, 5),
(6, 5, 2, 3, 6),
(7, 2, 1, 1, 7);

-- 11. Registers (teacher <-> student) ---------------------------------------
insert into Registers (TeacherID, StudentID, RegistrationDate) values
(1, 101, '2026-09-02'),
(1, 102, '2026-09-02'),
(1, 103, '2026-09-04'),
(2, 103, '2026-09-11'),
(2, 104, '2026-09-11'),
(3, 105, '2026-09-16'),
(3, 106, '2026-09-16'),
(4, 106, '2026-09-21');

-- 12. Includes (words used in each test) -------------------------------------
insert into Includes (TestID, FileID, WordNumber) values
(1, 1, 1), (1, 1, 2), (1, 1, 3), (1, 1, 4), (1, 1, 5),
(2, 1, 1), (2, 1, 2),
(3, 1, 1), (3, 1, 2), (3, 1, 3), (3, 1, 4), (3, 1, 5),
(4, 1, 3),
(5, 3, 1), (5, 3, 2), (5, 3, 3), (5, 3, 4), (5, 3, 5),
(6, 2, 1), (6, 2, 2), (6, 2, 3), (6, 2, 4), (6, 2, 5),
(7, 3, 2), (7, 3, 4);

-- 13. BelongsTo (incorrect word <-> group) -----------------------------------
insert into BelongsTo (IncorrectWordID, GroupID) values
(1, 1),
(2, 1),
(1, 2),
(2, 2),
(3, 3),
(5, 5),
(6, 5),
(6, 4);
