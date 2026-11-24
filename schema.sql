-- schema.sql : HW2 schema (no changes in HW3)
create database if not exists wordtest character set utf8mb4;
use wordtest;

create table Teacher(
	TeacherID int not null,
	FirstName varchar(25) not null,
	LastName varchar(25) not null,
	Email varchar(100) not null,
	Password varchar(300) not null,
	constraint PK_TeacherID primary key (TeacherID),
	constraint CH_Teacher_TeacherID check (TeacherID > 0), 
	constraint CH_Teacher_FirstName check (char_length(trim(FirstName)) > 0),
	constraint CH_Teacher_LastName check (char_length(trim(LastName)) > 0),
	constraint CH_Teacher_Email check (char_length(trim(Email)) > 0),
	constraint CH_Teacher_Password check (char_length(trim(Password)) > 0)
);

create table TeacherPhoneNumber(
	TeacherID int not null,
	PhoneNumber varchar(20) not null,
	constraint PK_TeacherID_PhoneNumber primary key (TeacherID, PhoneNumber),
	constraint FK_TeacherPhoneNumber_Teacher_TeacherID foreign key (TeacherID) references Teacher(TeacherID)
);

create table Student(
	StudentID int not null,
	FirstName varchar(25) not null,
	LastName varchar(25) not null,
	Email varchar(100) not null,
	Password varchar(300) not null,
	constraint PK_StudentID primary key (StudentID),
	constraint CH_Student_StudentID check (StudentID > 0),
	constraint CH_Student_FirstName check (char_length(trim(FirstName)) > 0),
	constraint CH_Student_LastName check (char_length(trim(LastName)) > 0),
	constraint CH_Student_Email check (char_length(trim(Email)) > 0),
	constraint CH_Student_Password check (char_length(trim(Password)) > 0)
);

create table StudentPhoneNumber(
	StudentID int not null,
	PhoneNumber varchar(20) not null,
	constraint PK_StudentID_PhoneNumber  primary key (StudentID, PhoneNumber),
	constraint FK_StudentPhoneNumber_Student_StudentID foreign key (StudentID) references Student(StudentID)
);

create table WordFile(
	FileID int not null,
	FileName varchar(100) not null,
	UploadDate date not null default (current_date),
	TeacherID int not null,
	constraint PK_FileID primary key (FileID),
	constraint FK_WordFile_Teacher_TeacherID foreign key (TeacherID) references Teacher(TeacherID),
	constraint CH_WordFile_FileID check (FileID > 0),
	constraint CH_WordFile_FileName check (char_length(trim(FileName)) > 0)
);

create table Word(
	FileID int not null,
	WordNumber int not null,
	WordContent varchar(200) not null,
	Meaning varchar(200) not null,
	constraint PK_FileID_WordNumber primary key (FileID, WordNumber),
	constraint FK_Word_WordFile_FileID foreign key (FileID) references WordFile(FileID),
	constraint CH_Word_WordNumber check (WordNumber > 0),
	constraint CH_Word_WordContent check (char_length(trim(WordContent)) > 0),
	constraint CH_Word_Meaning check (char_length(trim(Meaning)) > 0)
);

create table IncorrectWord(
	IncorrectWordID int not null,
	WrongCount int not null default (1),
	RegisterDate date not null default (current_date),
	FileID int not null,
	WordNumber int not null,
	StudentID int not null,
	constraint PK_IncorrectWordID primary key (IncorrectWordID),
	constraint FK_IncorrectWord_Word_FileID_WordNumber foreign key (FileID, WordNumber) references Word(FileID, WordNumber),
	constraint FK_IncorrectWord_Student_StudentID foreign key (StudentID) references Student(StudentID),
	constraint UQ_StudentID_FileID_WordNumber unique (StudentID, FileID, WordNumber),
	constraint CH_IncorrectWord_WrongCount check (WrongCount >= 1)
);

create table IncorrectWordGroup(
	GroupID int not null,
	GroupName varchar(30) not null default ('Incorrect Group'),
	GroupType enum('auto', 'manual') not null default ('manual'),
	CreateDate date not null default (current_date),
	FileID int,
	StudentID int not null,
	constraint PK_GroupID primary key (GroupID),
	constraint FK_IncorrectWordGroup_WordFile_FileID foreign key (FileID) references WordFile(FileID),
	constraint FK_IncorrectWordGroup_Student_StudentID foreign key (StudentID) references Student(StudentID),
	constraint CH_IncorrectWordGroup_GroupName check (char_length(trim(GroupName)) > 0),
	constraint CH_IncorrectWordGroup_GroupType_FileID check (GroupType = 'manual' or FileID is not null)
);

create table Test(
	TestID int not null,
	TestType enum('normal', 'wrong') not null,
	TestDate date not null default (current_date),
	StudentID int not null,
	GroupID int,
	constraint PK_TestID primary key (TestID),
	constraint FK_Test_Student_StudentID foreign key (StudentID) references Student(StudentID),
	constraint FK_Test_IncorrectWordGroup_GroupID foreign key (GroupID) references IncorrectWordGroup(GroupID),
	constraint CH_Test_TestType_GroupID check ((TestType = 'normal' and GroupID is null) or (TestType = 'wrong' and GroupID is not null))
);

create table TestResult(
	ResultID int not null,
	QuestionCount int not null,
	CorrectCount int not null default (0),
	IncorrectCount int not null default (0),
	TestID int not null,
	constraint PK_ResultID primary key (ResultID),
	constraint FK_TestResult_Test_TestID foreign key (TestID) references Test(TestID),
	constraint UQ_TestID unique (TestID),
	constraint CH_TestResult_QuestionCount check (QuestionCount > 0),
	constraint CH_TestResult_CorrectCount check (CorrectCount >= 0),
	constraint CH_TestResult_IncorrectCount check (IncorrectCount >= 0),
	constraint CH_TestResult_TotalCount check (CorrectCount + IncorrectCount = QuestionCount)
);

create table Registers(
	TeacherID int not null,
	StudentID int not null,
	RegistrationDate date not null default (current_date),
	constraint PK_TeacherID_StudentID primary key (TeacherID, StudentID),
	constraint FK_Registers_Teacher_TeacherID foreign key (TeacherID) references Teacher(TeacherID),
	constraint FK_Registers_Student_StudentID foreign key (StudentID) references Student(StudentID)
);

create table Includes(
	TestID int not null,
	FileID int not null,
	WordNumber int not null,
	constraint PK_TestID_FileID_WordNumber primary key (TestID, FileID, WordNumber),
	constraint FK_Includes_Test_TestID foreign key (TestID) references Test(TestID),
	constraint FK_Includes_Word_FileID_WordNumber foreign key (FileID, WordNumber) references Word(FileID, WordNumber)
);

create table BelongsTo(
	IncorrectWordID int not null,
	GroupID int not null,
	constraint PK_IncorrectWordID_GroupID primary key (IncorrectWordID, GroupID),
	constraint FK_BelongsTo_IncorrectWord_IncorrectWordID foreign key (IncorrectWordID) references IncorrectWord(IncorrectWordID),
	constraint FK_BelongsTo_IncorrectWordGroup_GroupID foreign key (GroupID) references IncorrectWordGroup(GroupID)
);
