"""Definitions for the "browse" and "add row" pages (one entry per table).

The SQL of every table is written out in full in the SQL dictionary below.
Every value the user types is passed to MySQL as a %s parameter.
"""


def F(name, label, kind = "text", **kw):
	"""One form field.
	kind: int | text | date | password | enum | select | word
	required : False for nullable columns (blank -> NULL)
	default  : True if the column has a DEFAULT (blank -> column is left out of the INSERT)
	"""
	field = dict(name = name, label = label, kind = kind, required = True, default = False,
		maxlen = None, options_sql = None, choices = None, suggest = False, cols = None, hint = "")
	field.update(kw)
	return field


# Korean headers shown on the pages (the SQL itself still uses the real column names)
COLUMN_LABELS = {
	"TeacherID": "교사 ID", "StudentID": "학생 ID",
	"FirstName": "이름", "LastName": "성", "Email": "이메일", "PhoneNumber": "전화번호",
	"FileID": "파일 ID", "FileName": "파일 이름", "UploadDate": "업로드 날짜",
	"WordNumber": "단어 번호", "WordContent": "단어", "Meaning": "뜻",
	"IncorrectWordID": "오답 단어 ID", "WrongCount": "오답 횟수", "RegisterDate": "등록 날짜",
	"GroupID": "그룹 ID", "GroupName": "그룹 이름", "GroupType": "그룹 유형", "CreateDate": "생성 날짜",
	"TestID": "시험 ID", "TestType": "시험 유형", "TestDate": "시험 날짜",
	"ResultID": "결과 ID", "QuestionCount": "문제 수", "CorrectCount": "정답 수",
	"IncorrectCount": "오답 수", "RegistrationDate": "등록 날짜",
}

TEACHER_OPT = ("SELECT TeacherID, CONCAT(TeacherID, '. ', FirstName, ' ', LastName) "
	"FROM Teacher ORDER BY TeacherID")
STUDENT_OPT = ("SELECT StudentID, CONCAT(StudentID, '. ', FirstName, ' ', LastName) "
	"FROM Student ORDER BY StudentID")
FILE_OPT = "SELECT FileID, CONCAT(FileID, '. ', FileName) FROM WordFile ORDER BY FileID"
WORD_OPT = ("SELECT CONCAT(w.FileID, '-', w.WordNumber), "
	"CONCAT(f.FileName, ' #', w.WordNumber, ' - ', w.WordContent) "
	"FROM Word w JOIN WordFile f ON f.FileID = w.FileID ORDER BY w.FileID, w.WordNumber")
INCORRECT_OPT = ("SELECT i.IncorrectWordID, "
	"CONCAT(i.IncorrectWordID, '. ', s.FirstName, ' - ', w.WordContent) "
	"FROM IncorrectWord i "
	"JOIN Student s ON s.StudentID = i.StudentID "
	"JOIN Word w ON w.FileID = i.FileID AND w.WordNumber = i.WordNumber "
	"ORDER BY i.IncorrectWordID")
GROUP_OPT = ("SELECT GroupID, CONCAT(GroupID, '. ', GroupName, ' (', GroupType, ')') "
	"FROM IncorrectWordGroup ORDER BY GroupID")
TEST_OPT = ("SELECT TestID, CONCAT(TestID, '. ', TestType, ' 시험 (', TestDate, ')') "
	"FROM Test ORDER BY TestID")


TABLES = {
	"Teacher": dict(
		label = "교사",
		desc = "단어 파일을 올리는 교사입니다. 교사 가입 페이지에서 전화번호와 함께 등록합니다.",
		pk = ["TeacherID"],
		register = "teacher",
		fields = [],
	),
	"TeacherPhoneNumber": dict(
		label = "교사 전화번호",
		desc = "교사의 전화번호입니다. 가입할 때 입력하며, 여기서 번호를 더 추가할 수 있습니다.",
		pk = ["TeacherID", "PhoneNumber"],
		fields = [
			F("TeacherID", "교사", "select", options_sql = TEACHER_OPT),
			F("PhoneNumber", "전화번호", maxlen = 20),
		],
	),
	"Student": dict(
		label = "학생",
		desc = "시험을 보는 학생입니다. 학생 가입 페이지에서 전화번호와 함께 등록합니다.",
		pk = ["StudentID"],
		register = "student",
		fields = [],
	),
	"StudentPhoneNumber": dict(
		label = "학생 전화번호",
		desc = "학생의 전화번호입니다. 가입할 때 입력하며, 여기서 번호를 더 추가할 수 있습니다.",
		pk = ["StudentID", "PhoneNumber"],
		fields = [
			F("StudentID", "학생", "select", options_sql = STUDENT_OPT),
			F("PhoneNumber", "전화번호", maxlen = 20),
		],
	),
	"WordFile": dict(
		label = "단어 파일",
		desc = "교사가 올린 단어 목록 파일입니다.",
		pk = ["FileID"],
		fields = [
			F("FileID", "파일 ID", "int", suggest = True),
			F("FileName", "파일 이름", maxlen = 100),
			F("UploadDate", "업로드 날짜", "date", default = True, hint = "비워 두면 오늘 날짜가 들어갑니다."),
			F("TeacherID", "교사", "select", options_sql = TEACHER_OPT),
		],
	),
	"Word": dict(
		label = "단어",
		desc = "단어 파일에 들어 있는 단어와 뜻입니다.",
		pk = ["FileID", "WordNumber"],
		fields = [
			F("FileID", "단어 파일", "select", options_sql = FILE_OPT),
			F("WordNumber", "단어 번호", "int"),
			F("WordContent", "단어", maxlen = 200),
			F("Meaning", "뜻", maxlen = 200),
		],
	),
	"IncorrectWord": dict(
		label = "오답 단어",
		desc = "학생이 틀린 단어와 틀린 횟수입니다.",
		pk = ["IncorrectWordID"],
		fields = [
			F("IncorrectWordID", "오답 단어 ID", "int", suggest = True),
			F("WrongCount", "오답 횟수", "int", default = True, hint = "비워 두면 1이 들어갑니다."),
			F("RegisterDate", "등록 날짜", "date", default = True, hint = "비워 두면 오늘 날짜가 들어갑니다."),
			F("Word", "단어", "word", options_sql = WORD_OPT, cols = ("FileID", "WordNumber")),
			F("StudentID", "학생", "select", options_sql = STUDENT_OPT),
		],
	),
	"IncorrectWordGroup": dict(
		label = "오답 그룹",
		desc = "오답 단어를 묶은 복습 그룹입니다. auto 그룹은 단어 파일이 필요합니다.",
		pk = ["GroupID"],
		fields = [
			F("GroupID", "그룹 ID", "int", suggest = True),
			F("GroupName", "그룹 이름", default = True, maxlen = 30,
				hint = "비워 두면 'Incorrect Group'이 들어갑니다."),
			F("GroupType", "그룹 유형", "enum", choices = ["auto", "manual"], default = True,
				hint = "비워 두면 manual이 들어갑니다."),
			F("CreateDate", "생성 날짜", "date", default = True, hint = "비워 두면 오늘 날짜가 들어갑니다."),
			F("FileID", "단어 파일", "select", required = False, options_sql = FILE_OPT,
				hint = "그룹 유형이 auto이면 반드시 선택해야 합니다."),
			F("StudentID", "학생", "select", options_sql = STUDENT_OPT),
		],
	),
	"BelongsTo": dict(
		label = "그룹 구성",
		desc = "어떤 오답 단어가 어떤 그룹에 속하는지 나타냅니다.",
		pk = ["IncorrectWordID", "GroupID"],
		fields = [
			F("IncorrectWordID", "오답 단어", "select", options_sql = INCORRECT_OPT),
			F("GroupID", "그룹", "select", options_sql = GROUP_OPT),
		],
	),
	"Test": dict(
		label = "시험",
		desc = "학생이 본 시험입니다. wrong 시험에는 오답 그룹이 필요합니다.",
		pk = ["TestID"],
		fields = [
			F("TestID", "시험 ID", "int", suggest = True),
			F("TestType", "시험 유형", "enum", choices = ["normal", "wrong"]),
			F("TestDate", "시험 날짜", "date", default = True, hint = "비워 두면 오늘 날짜가 들어갑니다."),
			F("StudentID", "학생", "select", options_sql = STUDENT_OPT),
			F("GroupID", "오답 그룹", "select", required = False, options_sql = GROUP_OPT,
				hint = "wrong 시험은 반드시 선택하고, normal 시험은 비워 둡니다."),
		],
	),
	"TestResult": dict(
		label = "시험 결과",
		desc = "시험 점수입니다. 정답 수 + 오답 수는 문제 수와 같아야 합니다.",
		pk = ["ResultID"],
		fields = [
			F("ResultID", "결과 ID", "int", suggest = True),
			F("QuestionCount", "문제 수", "int"),
			F("CorrectCount", "정답 수", "int", default = True, hint = "비워 두면 0이 들어갑니다."),
			F("IncorrectCount", "오답 수", "int", default = True, hint = "비워 두면 0이 들어갑니다."),
			F("TestID", "시험", "select", options_sql = TEST_OPT),
		],
	),
	"Registers": dict(
		label = "학생 등록",
		desc = "어떤 학생이 어떤 교사에게 등록되어 있는지 나타냅니다.",
		pk = ["TeacherID", "StudentID"],
		fields = [
			F("TeacherID", "교사", "select", options_sql = TEACHER_OPT),
			F("StudentID", "학생", "select", options_sql = STUDENT_OPT),
			F("RegistrationDate", "등록 날짜", "date", default = True, hint = "비워 두면 오늘 날짜가 들어갑니다."),
		],
	),
	"Includes": dict(
		label = "시험 출제 단어",
		desc = "시험에 어떤 단어가 출제되었는지 나타냅니다.",
		pk = ["TestID", "FileID", "WordNumber"],
		fields = [
			F("TestID", "시험", "select", options_sql = TEST_OPT),
			F("Word", "단어", "word", options_sql = WORD_OPT, cols = ("FileID", "WordNumber")),
		],
	),
}


# SQL for every table, written out in full.
#   count       : row count on the table list
#   select      : all rows of the table
#   insert      : INSERT statement; parameters are taken from insert_cols in this order
#                 (IFNULL(%s, ...) uses the column's DEFAULT when the field is left empty)
#   select_one  : the row that was just inserted (parameters = the pk columns, in order)
#   next_id     : suggested next ID for the first form field
SQL = {
	"Teacher": dict(
		count = "SELECT COUNT(*) AS cnt FROM Teacher",
		select = "SELECT TeacherID, FirstName, LastName, Email FROM Teacher ORDER BY TeacherID",
	),
	"TeacherPhoneNumber": dict(
		count = "SELECT COUNT(*) AS cnt FROM TeacherPhoneNumber",
		select = "SELECT TeacherID, PhoneNumber FROM TeacherPhoneNumber ORDER BY TeacherID, PhoneNumber",
		insert = "INSERT INTO TeacherPhoneNumber (TeacherID, PhoneNumber) VALUES (%s, %s)",
		insert_cols = ["TeacherID", "PhoneNumber"],
		select_one = "SELECT TeacherID, PhoneNumber FROM TeacherPhoneNumber WHERE TeacherID = %s AND PhoneNumber = %s",
	),
	"Student": dict(
		count = "SELECT COUNT(*) AS cnt FROM Student",
		select = "SELECT StudentID, FirstName, LastName, Email FROM Student ORDER BY StudentID",
	),
	"StudentPhoneNumber": dict(
		count = "SELECT COUNT(*) AS cnt FROM StudentPhoneNumber",
		select = "SELECT StudentID, PhoneNumber FROM StudentPhoneNumber ORDER BY StudentID, PhoneNumber",
		insert = "INSERT INTO StudentPhoneNumber (StudentID, PhoneNumber) VALUES (%s, %s)",
		insert_cols = ["StudentID", "PhoneNumber"],
		select_one = "SELECT StudentID, PhoneNumber FROM StudentPhoneNumber WHERE StudentID = %s AND PhoneNumber = %s",
	),
	"WordFile": dict(
		count = "SELECT COUNT(*) AS cnt FROM WordFile",
		select = "SELECT FileID, FileName, UploadDate, TeacherID FROM WordFile ORDER BY FileID",
		insert = "INSERT INTO WordFile (FileID, FileName, UploadDate, TeacherID) "
			"VALUES (%s, %s, IFNULL(%s, CURRENT_DATE), %s)",
		insert_cols = ["FileID", "FileName", "UploadDate", "TeacherID"],
		select_one = "SELECT FileID, FileName, UploadDate, TeacherID FROM WordFile WHERE FileID = %s",
		next_id = "SELECT COALESCE(MAX(FileID), 0) + 1 AS next_id FROM WordFile",
	),
	"Word": dict(
		count = "SELECT COUNT(*) AS cnt FROM Word",
		select = "SELECT FileID, WordNumber, WordContent, Meaning FROM Word ORDER BY FileID, WordNumber",
		insert = "INSERT INTO Word (FileID, WordNumber, WordContent, Meaning) VALUES (%s, %s, %s, %s)",
		insert_cols = ["FileID", "WordNumber", "WordContent", "Meaning"],
		select_one = "SELECT FileID, WordNumber, WordContent, Meaning FROM Word WHERE FileID = %s AND WordNumber = %s",
	),
	"IncorrectWord": dict(
		count = "SELECT COUNT(*) AS cnt FROM IncorrectWord",
		select = "SELECT IncorrectWordID, WrongCount, RegisterDate, FileID, WordNumber, StudentID "
			"FROM IncorrectWord ORDER BY IncorrectWordID",
		insert = "INSERT INTO IncorrectWord (IncorrectWordID, WrongCount, RegisterDate, FileID, WordNumber, StudentID) "
			"VALUES (%s, IFNULL(%s, 1), IFNULL(%s, CURRENT_DATE), %s, %s, %s)",
		insert_cols = ["IncorrectWordID", "WrongCount", "RegisterDate", "FileID", "WordNumber", "StudentID"],
		select_one = "SELECT IncorrectWordID, WrongCount, RegisterDate, FileID, WordNumber, StudentID "
			"FROM IncorrectWord WHERE IncorrectWordID = %s",
		next_id = "SELECT COALESCE(MAX(IncorrectWordID), 0) + 1 AS next_id FROM IncorrectWord",
	),
	"IncorrectWordGroup": dict(
		count = "SELECT COUNT(*) AS cnt FROM IncorrectWordGroup",
		select = "SELECT GroupID, GroupName, GroupType, CreateDate, FileID, StudentID "
			"FROM IncorrectWordGroup ORDER BY GroupID",
		insert = "INSERT INTO IncorrectWordGroup (GroupID, GroupName, GroupType, CreateDate, FileID, StudentID) "
			"VALUES (%s, IFNULL(%s, 'Incorrect Group'), IFNULL(%s, 'manual'), IFNULL(%s, CURRENT_DATE), %s, %s)",
		insert_cols = ["GroupID", "GroupName", "GroupType", "CreateDate", "FileID", "StudentID"],
		select_one = "SELECT GroupID, GroupName, GroupType, CreateDate, FileID, StudentID "
			"FROM IncorrectWordGroup WHERE GroupID = %s",
		next_id = "SELECT COALESCE(MAX(GroupID), 0) + 1 AS next_id FROM IncorrectWordGroup",
	),
	"BelongsTo": dict(
		count = "SELECT COUNT(*) AS cnt FROM BelongsTo",
		select = "SELECT IncorrectWordID, GroupID FROM BelongsTo ORDER BY IncorrectWordID, GroupID",
		insert = "INSERT INTO BelongsTo (IncorrectWordID, GroupID) VALUES (%s, %s)",
		insert_cols = ["IncorrectWordID", "GroupID"],
		select_one = "SELECT IncorrectWordID, GroupID FROM BelongsTo WHERE IncorrectWordID = %s AND GroupID = %s",
	),
	"Test": dict(
		count = "SELECT COUNT(*) AS cnt FROM Test",
		select = "SELECT TestID, TestType, TestDate, StudentID, GroupID FROM Test ORDER BY TestID",
		insert = "INSERT INTO Test (TestID, TestType, TestDate, StudentID, GroupID) "
			"VALUES (%s, %s, IFNULL(%s, CURRENT_DATE), %s, %s)",
		insert_cols = ["TestID", "TestType", "TestDate", "StudentID", "GroupID"],
		select_one = "SELECT TestID, TestType, TestDate, StudentID, GroupID FROM Test WHERE TestID = %s",
		next_id = "SELECT COALESCE(MAX(TestID), 0) + 1 AS next_id FROM Test",
	),
	"TestResult": dict(
		count = "SELECT COUNT(*) AS cnt FROM TestResult",
		select = "SELECT ResultID, QuestionCount, CorrectCount, IncorrectCount, TestID "
			"FROM TestResult ORDER BY ResultID",
		insert = "INSERT INTO TestResult (ResultID, QuestionCount, CorrectCount, IncorrectCount, TestID) "
			"VALUES (%s, %s, IFNULL(%s, 0), IFNULL(%s, 0), %s)",
		insert_cols = ["ResultID", "QuestionCount", "CorrectCount", "IncorrectCount", "TestID"],
		select_one = "SELECT ResultID, QuestionCount, CorrectCount, IncorrectCount, TestID "
			"FROM TestResult WHERE ResultID = %s",
		next_id = "SELECT COALESCE(MAX(ResultID), 0) + 1 AS next_id FROM TestResult",
	),
	"Registers": dict(
		count = "SELECT COUNT(*) AS cnt FROM Registers",
		select = "SELECT TeacherID, StudentID, RegistrationDate FROM Registers ORDER BY TeacherID, StudentID",
		insert = "INSERT INTO Registers (TeacherID, StudentID, RegistrationDate) "
			"VALUES (%s, %s, IFNULL(%s, CURRENT_DATE))",
		insert_cols = ["TeacherID", "StudentID", "RegistrationDate"],
		select_one = "SELECT TeacherID, StudentID, RegistrationDate FROM Registers "
			"WHERE TeacherID = %s AND StudentID = %s",
	),
	"Includes": dict(
		count = "SELECT COUNT(*) AS cnt FROM Includes",
		select = "SELECT TestID, FileID, WordNumber FROM Includes ORDER BY TestID, FileID, WordNumber",
		insert = "INSERT INTO Includes (TestID, FileID, WordNumber) VALUES (%s, %s, %s)",
		insert_cols = ["TestID", "FileID", "WordNumber"],
		select_one = "SELECT TestID, FileID, WordNumber FROM Includes "
			"WHERE TestID = %s AND FileID = %s AND WordNumber = %s",
	),
}
for _name, _sql in SQL.items():
	TABLES[_name].update(_sql)


# Sign-up pages: the user row and its phone numbers are saved together.
ROLES = {
	"teacher": dict(label = "교사", table = "Teacher", id_col = "TeacherID",
		phone_table = "TeacherPhoneNumber"),
	"student": dict(label = "학생", table = "Student", id_col = "StudentID",
		phone_table = "StudentPhoneNumber"),
}
