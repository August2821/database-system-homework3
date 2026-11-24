import os
import mysql.connector


def get_db():
	return mysql.connector.connect(
		host = os.environ.get("DB_HOST", "localhost"),
		user = os.environ.get("DB_USER", "flaskuser"),
		password = os.environ.get("DB_PASSWORD", "1234"),
		database = os.environ.get("DB_NAME", "wordtest"),
		charset = "utf8mb4"
	)
