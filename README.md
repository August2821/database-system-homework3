# HW3 – Word Test (Flask + MySQL)

HW2에서 만든 `wordtest` 데이터베이스에 연결한 Flask 웹 페이지입니다.
13개 테이블 모두 웹에서 조회(SELECT)하고 추가(INSERT)할 수 있습니다.
화면은 한국어로 되어 있고, 검색 결과가 없을 때의 "No results" 문구만 과제 조건에 맞춰 영어로 두었습니다.

## 주요 페이지

| 페이지 | 주소 | 기능 |
|--------|------|------|
| 전체 테이블 | `/tables` | 13개 테이블 목록과 행 수 |
| 테이블 조회 | `/table/<테이블명>` | 해당 테이블의 모든 행을 SELECT |
| 행 추가 | `/table/<테이블명>/new` | 테이블에 INSERT (Teacher, Student는 가입 페이지에서 처리) |
| 교사 가입 | `/register/teacher` | `Teacher`와 `TeacherPhoneNumber`를 한 트랜잭션으로 INSERT |
| 학생 가입 | `/register/student` | `Student`와 `StudentPhoneNumber`를 한 트랜잭션으로 INSERT |
| 단어 검색 | `/words` | 사용자 입력(검색어, 단어 파일 드롭다운)으로 SELECT |
| 통계 | `/stats` | JOIN + GROUP BY (교사별 단어 수, 학생별 시험 정답률) |
| 로그인 | `/login/teacher`, `/login/student` | 이메일과 비밀번호 확인 |

조회와 추가 페이지에는 "사용된 SQL" 박스가 있어서 실행된 SQL을 바로 볼 수 있습니다. 보고서 캡처에 활용하세요.

## 준비물

- Python 3.10 이상
- MySQL 8.0.16 이상 (CHECK 제약 조건과 `default (expression)` 문법 때문에 필요합니다)

## 설치 및 실행 방법

0. **저장소 내려받기**
   ```bash
   git clone https://github.com/August2821/database-system-homework3.git
   cd database-system-homework3
   ```
   (zip 파일로 받았다면 압축을 풀고 그 폴더에서 터미널을 열면 됩니다.)

1. **DB 사용자 만들기** (MySQL root 계정으로 실행)
   ```sql
   create user if not exists 'flaskuser'@'localhost' identified by '1234';
   ```

2. **스키마 생성과 샘플 데이터 입력**
   ```bash
   mysql -u root -p < schema.sql
   mysql -u root -p < data.sql
   ```
   이미 `wordtest` DB가 있다면 먼저 `drop database wordtest;`로 지운 뒤 실행하세요.

3. **권한 부여** (MySQL root 계정으로 실행)
   ```sql
   grant all privileges on wordtest.* to 'flaskuser'@'localhost';
   flush privileges;
   ```

4. **패키지 설치** (가상환경 사용을 권장합니다)
   ```bash
   python -m venv venv
   source venv/bin/activate        # 윈도우: venv\Scripts\activate
   pip install -r requirements.txt
   ```

5. **실행**
   ```bash
   python app.py
   ```
   브라우저에서 http://127.0.0.1:5000 으로 접속합니다.

DB 접속 정보는 `database.py`에 있습니다 (host `localhost`, user `flaskuser`, password `1234`, database `wordtest`).
환경 변수 `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`으로 바꿀 수도 있습니다.

## 샘플 계정

교사와 학생 샘플 계정의 비밀번호는 모두 `password123`입니다.
예: 교사 `minjun.kim@school.kr`, 학생 `yuna.han@student.kr`

## 에러 처리 확인 방법

입력칸에 브라우저 자체 검사를 일부러 넣지 않아서, DB 규칙에 걸린 결과를 그대로 확인할 수 있습니다.

- **가입 페이지**: 이미 있는 ID(예: `1`)를 입력하면 기본키 중복 오류가 납니다. ID를 비우면 NOT NULL 오류, 이름을 비우면 CHECK 오류가 납니다. 하나라도 실패하면 아무것도 저장되지 않습니다.
- **행 추가 페이지**
  - `Test`에서 유형을 `wrong`으로 하고 그룹을 비우면 CHECK 오류가 납니다.
  - `TestResult`에서 정답 수 + 오답 수가 문제 수와 다르면 CHECK 오류가 납니다.
  - `Word`에서 이미 있는 파일과 단어 번호를 넣으면 기본키 중복 오류가 납니다.
- 외래키 칸은 DB에 있는 값만 드롭다운으로 고르게 했습니다. 그래서 외래키 오류 대신, 필수 드롭다운을 비워 두면 NOT NULL 오류가 납니다.

## SQL 관련 참고

- 사용자가 입력한 값은 모두 `%s` 파라미터로 전달합니다. 문자열을 이어 붙이는 방식은 쓰지 않았습니다.
- 모든 SQL은 직접 작성했고 문자열을 조합해서 만들지 않습니다. 13개 테이블의 조회·추가 SQL은 `tables.py`의 `SQL`에, 가입·로그인 SQL은 `app.py`의 `ROLE_SQL`에, 검색·통계 SQL은 `app.py`의 각 함수 안에 적혀 있습니다.
- 추가 폼에서 비워 둔 기본값 칸(날짜, 오답 횟수 등)은 `IFNULL(%s, CURRENT_DATE)`처럼 SQL 안에서 기본값이 들어가게 했습니다.
- ORM은 사용하지 않았습니다.

## HW2 대비 변경 사항

- 스키마 변경 없음. `schema.sql`은 HW2 스키마에 `create database` 한 줄만 추가한 것입니다.
- 비밀번호는 평문으로 저장합니다 (과제용 단순 구현).
- 전화번호는 가입할 때 함께 입력받습니다. 웹 페이지에서는 최소 1개를 필수로 하며, 스키마 자체는 전화번호 없는 사용자도 허용합니다.

## 파일 구성

```
homework3
├── README.md
├── app.py
├── data.sql
├── database.py
├── requirements.txt
├── schema.sql
├── static
│   └── style.css
├── tables.py
└── templates
    ├── _table.html
    ├── base.html
    ├── index.html
    ├── login.html
    ├── login_teacher.html
    ├── register.html
    ├── register_teacher.html
    ├── search_words.html
    ├── stats.html
    ├── table_new.html
    ├── table_view.html
    └── tables.html
```
