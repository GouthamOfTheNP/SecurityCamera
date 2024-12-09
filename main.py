import random
import os
import sqlite3
import time
from flask import render_template, request, Flask, session, redirect, url_for, jsonify, abort
from flask.views import MethodView
from flask_cors import CORS
from wtforms import Form, StringField, PasswordField
from wtforms.fields.simple import SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo
from sendemailpy3 import send_gmail
import numpy as np
import cv2
import bcrypt
from db_functions import add_user, user_exists, create_users_db, verify_password, verify_email, create_devices_db

app = Flask(__name__)
CORS(app)
app.secret_key = os.urandom(24)
app.config["SESSION_TYPE"] = "memcache"
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

create_users_db()
create_devices_db()

user_frames = {}
alphabets = {'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5, 'f': 6, 'g': 7, 'h': 8, 'i': 9, 'j': 10, 'k': 11, 'l': 12, 'm': 13,
             'n': 14, 'o': 15, 'p': 16, 'q': 17, 'r': 18, 's': 19, 't': 20, 'u': 21, 'v': 22, 'w': 23, 'x': 24, 'y': 25,
             'z': 26, 'A': 27, 'B': 28, 'C': 29, 'D': 30, 'E': 31, 'F': 32, 'G': 33, 'H': 34, 'I': 35, 'J': 36, 'K': 37,
             'L': 38, 'M': 39, 'N': 40, 'O': 41, 'P': 42, 'Q': 43, 'R': 44, 'S': 45, 'T': 46, 'U': 47, 'V': 48, 'W': 49,
             'X': 50, 'Y': 51, 'Z': 52}
alpha_inverted = {v: k for k, v in alphabets.items()} | {v + 52: k for k, v in alphabets.items()}

rand_num = random.randint(100000, 10000000)


class MainPage(MethodView):
	def get(self):
		device_form = DeviceForm()
		if session.get('logged_in'):
			return render_template("index.html", username=session.get('username'), device_form=device_form)
		return render_template("index.html", device_form=device_form)

	def post(self):
		device_form = DeviceForm(request.form)
		device = str(device_form.device_id.data)
		error_code = "Device successfully added. If the information is correct, your device will start."
		try:
			connection = sqlite3.connect("users.db")
			cursor = connection.cursor()
			cursor.execute("UPDATE users SET devices=COALESCE(devices, '') || ? WHERE username=?",
			               (device + ",", session.get('username')))
			connection.commit()
			cursor.close()
			connection.close()

		except Exception as e:
			error_code = "Invalid username."
		return render_template("index.html", device_form=device_form, error_code=error_code)


class SignUpPage(MethodView):
	def get(self):
		signup_form = SignupForm()
		if session.get("logged_in"):
			previous_page = session.get('previous_page', '/')
			session.pop('previous_page', None)
			if previous_page != request.url:
				return redirect(previous_page)
			return redirect(url_for("main_page"))
		return render_template("signup.html", signup_form=signup_form)

	def post(self):
		signup_form = SignupForm(request.form)
		username = str(signup_form.username.data)
		password = str(signup_form.password.data)
		confirm_password = str(signup_form.confirm_password.data)
		email = str(signup_form.email.data)
		error_code = "Successfully registered"
		if not user_exists(username):
			if password == confirm_password:
				add_user(username, password, email)
				session['logged_in'] = True
				session['username'] = username
				time.sleep(2)
				previous_page = session.get('previous_page', '/')
				session.pop('previous_page', None)
				if previous_page != request.url:
					return redirect(previous_page)
				return redirect(url_for("main_page"))
			else:
				error_code = "Passwords do not match"
		else:
			error_code = "Username already exists"
		return render_template("signup.html", signup_form=signup_form, error_code=error_code)


class LoginPage(MethodView):
	def get(self):
		if session.get("logged_in"):
			previous_page = session.get('previous_page', '/')
			session.pop('previous_page', None)
			if previous_page != request.url:
				return redirect(previous_page)
			return redirect(url_for("main_page"))
		login_form = LoginForm()
		return render_template("login.html", login_form=login_form)

	def post(self):
		login_form = LoginForm(request.form)
		username = str(login_form.username.data)
		password = str(login_form.password.data)
		error_code = "Successfully logged in"
		try:
			try:
				if verify_password(username, password):
					session['logged_in'] = True
					session['username'] = username
					time.sleep(2)
					previous_page = session.get('previous_page', '/')
					session.pop('previous_page', None)
					if previous_page != request.url:
						return redirect(previous_page)
					return redirect(url_for("main_page"))
			except TypeError as e:
				error_code = "Invalid username or password"
		except TypeError as e:
			error_code = "An error occurred while logging in. Please try again."
		return render_template("login.html", login_form=login_form, error_code=error_code)


class ForgotPage(MethodView):
	def get(self):
		forgot_form = ForgotForm()
		return render_template("forgot.html", forgot_form=forgot_form)

	def post(self):
		forgot_form = ForgotForm(request.form)
		email = str(forgot_form.email.data)
		error_code = "Email successfully sent"
		verification_tuple = verify_email(email)
		connection = sqlite3.connect('users.db')
		cursor = connection.cursor()
		cursor.execute("SELECT username FROM users WHERE email=?", (email,))
		result = cursor.fetchone()
		if result is not None:
			username = username_hash(result[0], random.randint(0, 45))
		connection.commit()
		cursor.close()
		connection.close()
		if verification_tuple[0]:
			session["reset_token"] = True
			send_gmail("Password Reset", f"Password reset link for Vigilance Solutions: {request.url_root.rstrip('/') + url_for('reset_page', user=username)}", verification_tuple[1], os.getenv("USERNAME_SENDER"), os.getenv("PASSWORD_SENDER"))
		else:
			error_code = "Invalid email address"
		return render_template("forgot.html", forgot_form=forgot_form, error_code=error_code)


class ResetPage(MethodView):
	def get(self, user):
		reset_form = ResetForm()
		if user != "<user>":
			user = username_decrypt(user)
		try:
			return render_template("reset.html", reset_form=reset_form, user=user)
		except Exception as e:
			return abort(404)

	def post(self, user):
		if user != "<user>":
			user = username_decrypt(user)
		reset_form = ResetForm(request.form)
		try:
			password = str(reset_form.password.data)
			connection = sqlite3.connect("users.db")
			cursor = connection.cursor()
			cursor.execute("UPDATE users SET password=? WHERE username=?",
			               (bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()), user))
			connection.commit()
			cursor.close()
			connection.close()
			error_code = "Password successfully reset"
			return render_template("reset.html", reset_form=reset_form, user=user, error_code=error_code)
		except Exception as e:
			error_code = "An error occurred while resetting the password. Please try again."
			return render_template("reset.html", reset_form=reset_form, user=user, error_code=error_code)


class MobileAppPage(MethodView):
	def get(self):
		return render_template("mobile_app.html")


class LogoutPage(MethodView):
	def get(self):
		try:
			session.pop('logged_in', None)
			session.pop('username', None)
			time.sleep(1)
			previous_page = session.get('previous_page', '/')
			session.pop('previous_page', None)
			if previous_page != request.url:
				return redirect(previous_page)
			return redirect(url_for("main_page"))
		except Exception:
			return render_template('logout.html')

	def post(self):
		previous_page = session.get('previous_page', '/')
		session.pop('previous_page', None)
		if previous_page != request.url:
			return redirect(previous_page)
		return redirect(url_for("main_page"))


class SecurityCameraPage(MethodView):
	def get(self):
		connection = sqlite3.connect("devices.db")
		cursor = connection.cursor()
		cursor.execute("SELECT device, stock, price, image, identifier FROM devices")
		results = cursor.fetchall()
		connection.commit()
		connection.close()
		data = [
			{"device": result[0], "stock": result[1], "price": result[2], "image": result[3], "identifier": result[4]}
			for result in results
		]
		return render_template("security_camera.html", data=data)


class PrivacyPage(MethodView):
	def get(self):
		return render_template("privacy.html")


class ProductPageInd(MethodView):
	def get(self, product_id):
		connection = sqlite3.connect("devices.db")
		cursor = connection.cursor()
		cursor.execute("SELECT device, stock, price, description, image FROM devices where identifier = ?",
		               (product_id,))
		results = cursor.fetchone()
		connection.commit()
		connection.close()
		data = {"device": results[0], "stock": results[1], "price": results[2], "description": results[3],
		        "image": results[4]}
		return render_template("product.html", data=data)


@app.route('/stream/b8ac99d7d8a6feb99896856d7b67b6d4df6da18d/5ee174eb9985595de358d51f3c8dfd9e2fd72e6a'
           '/caa383196608a0d23ebb2158cb3807a6bd760b6364c6a8b26d1f5c54888242a9/<user_id>')
def stream(user_id):
	if user_frames:
		_, buffer = cv2.imencode('.jpg', user_frames[user_id])
		return buffer.tobytes(), 200, {'Content-Type': 'image/jpeg'}
	return "No frames available", 404


@app.route('/57152cbec2b16cbbfca4b135ab57740b83a47bcb/upload_frame', methods=['POST'])
def upload_frame():
	user_id = request.form.get('user_id')
	if 'frame' not in request.files:
		return "No frame found", 400

	frame = request.files['frame'].read()

	np_frame = np.frombuffer(frame, np.uint8)
	image = cv2.imdecode(np_frame, cv2.IMREAD_COLOR)

	if user_id:
		user_frames[user_id] = image

	return "Frame received", 200


@app.route('/478cb55db6df5b5b4f9d38e081161edf/3ec984b8ebcb95979aafc140ab3175f7/afb3132ee624f40beae950c57ae0f3a5'
           '/5f16518ece37398319606c81556fc42b', methods=['POST'])
def get_devices():
	metadata_key = request.headers.get('X-Metadata-Key')
	if metadata_key:
		if metadata_key == str(rand_num):
			connection = sqlite3.connect("users.db")
			cursor = connection.cursor()
			cursor.execute("SELECT username, email, devices FROM users")
			devices = cursor.fetchall()
			connection.close()
			return jsonify(devices)
		else:
			return jsonify({"error": "Invalid metadata key"}), 401
	else:
		return jsonify({"error": "Metadata key missing"}), 400


@app.route('/5f16518ece37398319606c81556fc42b/key_generator/<username>/<password>')
def key_generator(username, password):
	valid_users = ("exfkey", "cxvkey")
	valid_passwords = ("rrfcelDkey345", "445jgjdakeyfnk")
	if username in valid_users and password in valid_passwords:
		return jsonify(rand_num)
	return abort(404)


@app.before_request
def store_previous_page():
	if (request.endpoint is not None and request.endpoint not in
			['login_page', 'signup_page', 'logout_page', 'forgot_page'] and not request.endpoint.startswith('static')
			and request.method == 'GET' and not "/stream/b8ac99d7d8a6feb99896856d7b67b6d4df6da18d"
			                                    "/5ee174eb9985595de358d51f3c8dfd9e2fd72e6a"
			                                    "/caa383196608a0d23ebb2158cb3807a6bd760b6364c6a8b26d1f5c54888242a9/"
			                                    in request.url):
		session['previous_page'] = request.url


def username_hash(username, salt):
	username = list(username)

	for i in range(len(username)):
		username[i] = (alphabets[username[i]] + salt)
	for i in range(len(username)):
		username[i] = alpha_inverted[username[i]]
	for i in range(len(list(str(salt)))):
		username.insert(random.randint(0, len(username)), list(str(salt))[i])
	return ''.join(username)


def username_decrypt(username):
	salt = []
	username = list(username)
	for char in username[:]:
		if char.isdigit():
			salt.append(username.pop(username.index(char)))
	salt = int(''.join(salt))
	alpha_decrypt = {k: v + (52 if v <= salt else 0) for k, v in alphabets.items()}

	decrypted_username = []
	for char in username:
		decrypted_value = (alpha_decrypt[char] - salt)
		decrypted_username.append(alpha_inverted[decrypted_value])

	return ''.join(decrypted_username)


class SignupForm(Form):
	email = StringField("Email: ", validators=[DataRequired(), Email()])
	username = StringField("Username: ", validators=[DataRequired()])
	password = PasswordField("Password: ", validators=[DataRequired(),
	                                                   Length(min=8,
	                                                          message="Password must be at least 8 characters long")])
	confirm_password = PasswordField("Confirm Password: ",
	                                 validators=[DataRequired(),
	                                             EqualTo('password', message="Passwords must match")])
	submit = SubmitField("Submit")


class LoginForm(Form):
	username = StringField("Username: ", validators=[DataRequired()])
	password = PasswordField("Password: ", validators=[DataRequired()])
	submit = SubmitField("Submit")


class ForgotForm(Form):
	email = StringField("Email: ", validators=[DataRequired(), Email()])
	submit = SubmitField("Submit")


class ResetForm(Form):
	password = PasswordField("New Password: ", validators=[DataRequired(),
	                                                       Length(min=8,
	                                                              message="Password must be at least 8 characters long")])
	confirm_password = PasswordField("Confirm Password: ",
	                                 validators=[DataRequired(),
	                                             EqualTo('password', message="Passwords must match")])
	submit = SubmitField("Submit")


class DeviceForm(Form):
	device_id = StringField("Device ID: ", validators=[DataRequired(), Length(min=14, message="Device ID must be at "
	                                                                                          "least 14 characters long")])
	submit = SubmitField("Submit")


app.add_url_rule('/', view_func=MainPage.as_view('main_page'))
app.add_url_rule('/signup', view_func=SignUpPage.as_view('signup_page'))
app.add_url_rule('/login', view_func=LoginPage.as_view('login_page'))
app.add_url_rule('/forgot', view_func=ForgotPage.as_view('forgot_page'))
app.add_url_rule('/mobile-app', view_func=MobileAppPage.as_view('mobile_app_page'))
app.add_url_rule('/security-camera', view_func=SecurityCameraPage.as_view('security_camera_page'))
app.add_url_rule('/logout', view_func=LogoutPage.as_view('logout_page'))
app.add_url_rule('/privacy', view_func=PrivacyPage.as_view('privacy_page'))
app.add_url_rule('/product/<product_id>', view_func=ProductPageInd.as_view('product_page_ind'))
app.add_url_rule('/reset/<user>', view_func=ResetPage.as_view('reset_page'))

if __name__ == '__main__':
	app.run(debug=True)
