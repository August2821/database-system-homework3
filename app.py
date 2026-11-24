import re
from flask import Flask, render_template, request, redirect, url_for, abort
from markupsafe import Markup, escape
from mysql.connector import Error as MySQLError
from database import get_db
from tables import TABLES, ROLES, COLUMN_LABELS

app = Flask(__name__)

PHONE_RE = re.compile(r"[0-9+\-\s]{7,20}")


@app.template_filter("highlight")
def highlight(value, keyword = ""):
	"""Wrap matches of keyword in <mark>; everything else is HTML-escaped."""
	if value is None:
		return Markup('<span class="null">NULL</span>')
	text = str(value)
	if not keyword:
		return escape(text)
	pattern = re.compile(re.escape(keyword), re.IGNORECASE)
	out, last = Markup(""), 0
	for m in pattern.finditer(text):
		out += escape(text[last:m.start()]) + Markup("<mark>") + escape(m.group(0)) + Markup("</mark>")
		last = m.end()
	return out + escape(text[last:])


@app.template_filter("col_label")
def col_label(name):
	"""Korean header for a column name (other names are shown as they are)."""
	return COLUMN_LABELS.get(name, name)


def run_select(sql, params = ()):
	"""Run a parameterized SELECT and return (column_names, rows as dicts)."""
	conn = get_db()
	try:
		cursor = conn.cursor(dictionary = True)
		cursor.execute(sql, params)
		rows = cursor.fetchall()
		columns = [d[0] for d in cursor.description]
		cursor.close()
		return columns, rows
	finally:
		conn.close()


def friendly_error(err):
	"""Turn a MySQL error into a message a user can act on."""
	messages = {
		1062: "이미 존재하는 값입니다. 기본키(또는 중복 불가 항목)가 중복되었습니다. (Duplicate entry)",
		1048: "비어 있으면 안 되는 항목이 있습니다. 필수 칸을 모두 입력해 주세요. (NOT NULL violation)",
		3819: "입력값이 테이블 규칙(CHECK)에 맞지 않습니다. (Check constraint violated)",
		1452: "참조하는 값이 존재하지 않습니다. 목록에서 올바른 항목을 선택해 주세요. (Foreign key violation)",
		1406: "입력값이 너무 깁니다. 글자 수 제한을 확인해 주세요. (Data too long)",
		1292: "날짜 또는 숫자 형식이 올바르지 않습니다. (Incorrect value)",
	}
	base = messages.get(err.errno, "데이터베이스 오류가 발생했습니다.")
	detail = getattr(err, "msg", str(err))
	return f"{base} [{detail}]"


# ---------------------------------------------------------------- home
@app.route("/")
def home():
	return render_template("index.html")


# ------------------------------------------------ browse every table
@app.route("/tables")
def tables_index():
	items, error = [], None
	try:
		for name, cfg in TABLES.items():
			_, rows = run_select(cfg["count"])
			items.append((name, cfg, rows[0]["cnt"]))
	except MySQLError as e:
		error = friendly_error(e)
	return render_template("tables.html", items = items, error = error)


@app.route("/table/<name>")
def table_view(name):
	cfg = TABLES.get(name)
	if cfg is None:
		abort(404)
	sql = cfg["select"]
	columns, rows, error = [], [], None
	try:
		columns, rows = run_select(sql)
	except MySQLError as e:
		error = friendly_error(e)
	return render_template("table_view.html", name = name, cfg = cfg, sql = sql,
		columns = columns, rows = rows, error = error)


# ------------------------------------------------- insert into any table
def convert_form(cfg, form):
	"""Read the form into {column: value}. Returns (values, raw, shown, error)."""
	values, raw, shown, error = {}, {}, {}, None
	for f in cfg["fields"]:
		name, kind = f["name"], f["kind"]
		text = form.get(name, "")
		text = text if kind == "password" else text.strip()
		raw[name] = text

		if text == "":
			if f["default"]:
				continue                       # leave it out, MySQL uses the DEFAULT
			value = None if kind in ("int", "date", "select", "word", "enum") or not f["required"] else ""
			if kind == "word":
				for c in f["cols"]:
					values[c] = None
			else:
				values[name] = value
			continue

		try:
			if kind in ("int", "select"):
				values[name] = int(text)
			elif kind == "word":
				file_id, word_no = text.split("-")
				values[f["cols"][0]], values[f["cols"][1]] = int(file_id), int(word_no)
			elif kind == "enum":
				if text not in f["choices"]:
					raise ValueError
				values[name] = text
			elif kind == "password":
				values[name] = text
			else:
				values[name] = text
		except ValueError:
			error = f"'{f['label']}' 값이 올바르지 않습니다."
	return values, raw, shown, error


@app.route("/table/<name>/new", methods = ["GET", "POST"])
def table_new(name):
	cfg = TABLES.get(name)
	if cfg is None:
		abort(404)
	if cfg.get("register"):
		return redirect(url_for("register", role = cfg["register"]))

	options, raw, error = {}, {}, None
	new_cols, new_rows, run_sql, run_params = [], [], None, []

	try:
		for f in cfg["fields"]:
			if f["options_sql"]:
				_, rows = run_select(f["options_sql"])
				options[f["name"]] = [tuple(str(v) for v in r.values()) for r in rows]
		for f in cfg["fields"]:
			raw[f["name"]] = ""
			if f["suggest"] and request.method == "GET":
				_, r = run_select(cfg["next_id"])
				raw[f["name"]] = str(r[0]["next_id"])
	except MySQLError as e:
		error = friendly_error(e)

	if request.method == "POST" and error is None:
		values, raw, shown, error = convert_form(cfg, request.form)
		if error is None:
			run_sql = cfg["insert"]
			params = [values.get(c) for c in cfg["insert_cols"]]    # empty -> None -> DEFAULT / NULL
			run_params = ["NULL" if v is None else v for v in params]
			conn = get_db()
			try:
				cursor = conn.cursor()
				cursor.execute(run_sql, params)
				conn.commit()
				cursor.close()
				new_cols, new_rows = run_select(cfg["select_one"], [values[c] for c in cfg["pk"]])
				raw = {k: "" for k in raw}      # clear the form after success
			except MySQLError as e:
				conn.rollback()
				error = friendly_error(e)
			finally:
				conn.close()

	return render_template("table_new.html", name = name, cfg = cfg, options = options, raw = raw,
		error = error, new_cols = new_cols, new_rows = new_rows, sql = run_sql, params = run_params)


# SQL for sign-up and login, written out in full for each role
ROLE_SQL = {
	"teacher": dict(
		insert_user = """INSERT INTO Teacher (TeacherID, FirstName, LastName, Email, Password)
			VALUES (%s, %s, %s, %s, %s)""",
		insert_phone = "INSERT INTO TeacherPhoneNumber (TeacherID, PhoneNumber) VALUES (%s, %s)",
		select_new = """SELECT u.TeacherID, u.FirstName, u.LastName, u.Email,
			       GROUP_CONCAT(p.PhoneNumber ORDER BY p.PhoneNumber SEPARATOR ', ') AS `전화번호`
			FROM Teacher u
			LEFT JOIN TeacherPhoneNumber p ON p.TeacherID = u.TeacherID
			WHERE u.TeacherID = %s
			GROUP BY u.TeacherID, u.FirstName, u.LastName, u.Email""",
		login = "SELECT * FROM Teacher WHERE Email = %s",
	),
	"student": dict(
		insert_user = """INSERT INTO Student (StudentID, FirstName, LastName, Email, Password)
			VALUES (%s, %s, %s, %s, %s)""",
		insert_phone = "INSERT INTO StudentPhoneNumber (StudentID, PhoneNumber) VALUES (%s, %s)",
		select_new = """SELECT u.StudentID, u.FirstName, u.LastName, u.Email,
			       GROUP_CONCAT(p.PhoneNumber ORDER BY p.PhoneNumber SEPARATOR ', ') AS `전화번호`
			FROM Student u
			LEFT JOIN StudentPhoneNumber p ON p.StudentID = u.StudentID
			WHERE u.StudentID = %s
			GROUP BY u.StudentID, u.FirstName, u.LastName, u.Email""",
		login = "SELECT * FROM Student WHERE Email = %s",
	),
}


# ------------------------------------- sign-up (user + phone numbers)
@app.route("/register/<role>", methods = ["GET", "POST"])
def register(role):
	r = ROLES.get(role)
	if r is None:
		abort(404)
	id_col = r["id_col"]
	sql = ROLE_SQL[role]

	form = {"id": "", "FirstName": "", "LastName": "", "Email": ""}
	phones = [""]
	error, new_cols, new_rows = None, [], []

	if request.method == "POST":
		form = {k: request.form.get(k, "").strip() for k in form}
		password = request.form.get("password", "")
		phones = [p.strip() for p in request.form.getlist("PhoneNumber")] or [""]
		phone_list = list(dict.fromkeys(p for p in phones if p))   # no blanks, no duplicates

		user_id = None
		if form["id"]:
			if form["id"].isdigit():
				user_id = int(form["id"])
			else:
				error = f"{COLUMN_LABELS[id_col]}는 숫자로 입력해 주세요."
		if error is None and not phone_list:
			error = "전화번호를 1개 이상 입력해 주세요."
		if error is None and not all(PHONE_RE.fullmatch(p) for p in phone_list):
			error = "전화번호는 숫자, 하이픈(-), +만 사용할 수 있고 7~20자여야 합니다."

		if error is None:
			conn = get_db()
			try:
				cursor = conn.cursor()
				cursor.execute(sql["insert_user"],
					(user_id, form["FirstName"], form["LastName"], form["Email"], password))
				for p in phone_list:
					cursor.execute(sql["insert_phone"], (user_id, p))
				conn.commit()      # user and phones are saved together, or not at all
				cursor.close()
				new_cols, new_rows = run_select(sql["select_new"], (user_id,))
				form = {k: "" for k in form}
				phones = [""]
			except MySQLError as e:
				conn.rollback()
				error = friendly_error(e)
			finally:
				conn.close()

	return render_template("register.html", role = role, label = r["label"], id_label = COLUMN_LABELS[id_col],
		form = form, phones = phones, error = error, new_cols = new_cols, new_rows = new_rows)


# --------------------------------------------------------------- login
@app.route("/login/<role>", methods = ["GET", "POST"])
def login(role):
	r = ROLES.get(role)
	if r is None:
		abort(404)
	message, ok = None, False
	if request.method == "POST":
		email = request.form.get("Email", "").strip()
		password = request.form.get("password", "")
		try:
			_, rows = run_select(ROLE_SQL[role]["login"], (email,))
			if rows and rows[0]["Password"] == password:
				message, ok = f"환영합니다, {rows[0]['FirstName']}님!", True
			else:
				message = "이메일 또는 비밀번호가 올바르지 않습니다."
		except MySQLError as e:
			message = friendly_error(e)
	return render_template("login.html", role = role, label = r["label"], message = message, ok = ok)


# ------------------------------------------------- SELECT 1: search words
@app.route("/words")
def search_words():
	keyword = request.args.get("q", "").strip()
	file_id = request.args.get("file_id", "0")
	file_id = int(file_id) if file_id.isdigit() else 0
	searched = "q" in request.args or "file_id" in request.args

	error = None
	files = []
	columns, rows = [], []
	try:
		_, files = run_select("SELECT FileID, FileName FROM WordFile ORDER BY FileID")
		if searched:
			sql = """
				SELECT f.FileName AS `단어 파일`, w.WordNumber AS `번호`,
				       w.WordContent AS `단어`, w.Meaning AS `뜻`
				FROM Word w
				JOIN WordFile f ON f.FileID = w.FileID
				WHERE (%s = 0 OR w.FileID = %s)
				  AND (w.WordContent LIKE %s OR w.Meaning LIKE %s)
				ORDER BY w.FileID, w.WordNumber"""
			like = f"%{keyword}%"
			columns, rows = run_select(sql, (file_id, file_id, like, like))
	except MySQLError as e:
		error = friendly_error(e)

	return render_template("search_words.html", files = files, keyword = keyword,
		file_id = file_id, searched = searched, columns = columns, rows = rows, error = error)


# -------------------------------------- SELECT 2: JOIN + GROUP BY reports
@app.route("/stats")
def stats():
	error = None
	teacher_cols, teacher_rows = [], []
	student_cols, student_rows = [], []
	try:
		# JOIN (3 tables) + GROUP BY : files and words per teacher
		teacher_sql = """
			SELECT t.TeacherID AS `교사 ID`,
			       CONCAT(t.FirstName, ' ', t.LastName) AS `교사`,
			       COUNT(DISTINCT f.FileID) AS `단어 파일 수`,
			       COUNT(w.WordNumber) AS `총 단어 수`
			FROM Teacher t
			LEFT JOIN WordFile f ON f.TeacherID = t.TeacherID
			LEFT JOIN Word w ON w.FileID = f.FileID
			GROUP BY t.TeacherID, t.FirstName, t.LastName
			ORDER BY `총 단어 수` DESC, t.TeacherID"""
		teacher_cols, teacher_rows = run_select(teacher_sql)

		# JOIN (3 tables) + GROUP BY : test performance per student
		student_sql = """
			SELECT s.StudentID AS `학생 ID`,
			       CONCAT(s.FirstName, ' ', s.LastName) AS `학생`,
			       COUNT(t.TestID) AS `응시 횟수`,
			       SUM(r.CorrectCount) AS `정답 수`,
			       SUM(r.QuestionCount) AS `문제 수`,
			       ROUND(SUM(r.CorrectCount) / SUM(r.QuestionCount) * 100, 1) AS `정답률`
			FROM Student s
			JOIN Test t ON t.StudentID = s.StudentID
			JOIN TestResult r ON r.TestID = t.TestID
			GROUP BY s.StudentID, s.FirstName, s.LastName
			ORDER BY `정답률` DESC"""
		student_cols, student_rows = run_select(student_sql)
	except MySQLError as e:
		error = friendly_error(e)

	return render_template("stats.html", teacher_cols = teacher_cols, teacher_rows = teacher_rows,
		student_cols = student_cols, student_rows = student_rows, error = error)


if __name__ == "__main__":
	app.run(debug = True)
