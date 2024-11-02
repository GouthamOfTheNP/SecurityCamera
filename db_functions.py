import sqlite3
import bcrypt


def create_table():
	connection = sqlite3.connect("users.db")
	connection.row_factory = sqlite3.Row
	cursor = connection.cursor()
	with connection:
		cursor.execute("CREATE TABLE IF NOT EXISTS users "
		               "(username TEXT NOT NULL, password TEXT NOT NULL, email TEXT NOT NULL, devices TEXT NOT NULL)")
		connection.commit()


def user_exists(username):
	connection = sqlite3.connect("users.db")
	connection.row_factory = sqlite3.Row
	cursor = connection.cursor()
	cursor.execute('SELECT username FROM users WHERE username = ?', (username,))
	fetch_one = cursor.fetchone()
	connection.close()
	return fetch_one is not None


def add_user(username, password, email):
	connection = sqlite3.connect("users.db")
	connection.row_factory = sqlite3.Row
	cursor = connection.cursor()
	cursor.execute(
		"INSERT INTO users (username, password, email, devices) VALUES (?, ?, ?, ?)",
		(username, bcrypt.hashpw(password.encode(), bcrypt.gensalt()), email, None))
	connection.commit()
	connection.close()


def verify_password(username, password):
	connection = sqlite3.connect("users.db")
	connection.row_factory = sqlite3.Row
	cursor = connection.cursor()
	cursor.execute('SELECT password FROM users WHERE username = ?', (username,))
	fetch_one = cursor.fetchone()
	connection.close()
	return bcrypt.checkpw(password.encode(), fetch_one[0])


def verify_email(email):
	connection = sqlite3.connect("users.db")
	connection.row_factory = sqlite3.Row
	cursor = connection.cursor()
	cursor.execute('SELECT email FROM users WHERE email = ?', (email,))
	fetch_one = cursor.fetchone()
	connection.close()
	return fetch_one is not None, fetch_one[0] if fetch_one else None


def update_devices(device, username):
	connection = sqlite3.connect("users.db")
	connection.row_factory = sqlite3.Row
	cursor = connection.cursor()
	cursor.execute("UPDATE users SET devices = ? WHERE username = ?", (device, username))
	connection.commit()


def create_devices_db():
	connection = sqlite3.connect("devices.db")
	connection.row_factory = sqlite3.Row
	cursor = connection.cursor()
	with connection:
		cursor.execute("CREATE TABLE IF NOT EXISTS devices"
		               "(id INTEGER PRIMARY KEY AUTOINCREMENT, device TEXT NOT NULL, "
		               "stock TEXT NOT NULL, identifier TEXT NOT NULL, image TEXT NOT NULL)")
	connection.commit()
	connection.close()