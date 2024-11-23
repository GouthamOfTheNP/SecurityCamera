import random
from datetime import datetime
from db_functions import add_user, user_exists, create_users_db, verify_password, verify_email, create_devices_db
from flask import render_template, request, Flask, session, redirect, url_for, jsonify, abort
from flask.views import MethodView
from flask_cors import CORS
from wtforms import Form, StringField, IntegerField, BooleanField
from wtforms.fields.simple import SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo
from sendemailpy3 import send_gmail
import os
import sqlite3
import time
import numpy as np
import cv2
import requests
import threading

app = Flask(__name__)
CORS(app)
app.secret_key = os.urandom(24)
app.config["SESSION_TYPE"] = "memcache"
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

create_users_db()
create_devices_db()

user_frames = {}

rand_num = random.randint(100000, 10000000)


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


class MainPage(MethodView):
	def get(self):
		if session.get('logged_in'):
			return render_template("index.html", username=session.get('username'))
		return render_template("index.html")


@app.route('/stream/b8ac99d7d8a6feb99896856d7b67b6d4df6da18d/5ee174eb9985595de358d51f3c8dfd9e2fd72e6a'
           '/caa383196608a0d23ebb2158cb3807a6bd760b6364c6a8b26d1f5c54888242a9/<user_id>')
def stream(user_id):
	if user_frames:
		_, buffer = cv2.imencode('.jpg', user_frames[user_id])
		return buffer.tobytes(), 200, {'Content-Type': 'image/jpeg'}
	return "No frames available", 404


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
		if verification_tuple[0]:
			session["reset_token"] = True
			send_gmail("Password Reset",
			           "Your password has been reset. Please login with your new password.",
			           verification_tuple[1], os.getenv("USERNAME_SENDER"), os.getenv("PASSWORD_SENDER"))
		else:
			error_code = "Invalid email address"
		return render_template("forgot.html", forgot_form=forgot_form, error_code=error_code)


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
		cursor.execute("SELECT device, stock, image FROM devices")
		results = cursor.fetchall()
		connection.commit()
		connection.close()
		data = [
			{"device": result[0], "stock": result[1], "image": result[2]}
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
		cursor.execute("SELECT device, stock, image FROM devices where identifier = ?", (product_id,))
		results = cursor.fetchone()
		connection.commit()
		connection.close()
		data = {"device": results[0], "stock": results[1], "image": results[2]}
		return render_template("product.html", data=data)


@app.route('/478cb55db6df5b5b4f9d38e081161edf/3ec984b8ebcb95979aafc140ab3175f7/afb3132ee624f40beae950c57ae0f3a5'
           '/5f16518ece37398319606c81556fc42b/<key>')
def get_devices(key):
	if int(key) == requests.get(f"{request.host_url.rstrip('/')}/5f16518ece37398319606c81556fc42b/key_generator/exfkey"
	                            "/445jgjdakeyfnk").json():
		connection = sqlite3.connect("users.db")
		cursor = connection.cursor()
		cursor.execute("SELECT username, devices FROM users")
		devices = cursor.fetchall()
		connection.close()
		return jsonify(devices)
	return jsonify({"error": "Invalid credentials"}), 401


lock = threading.Lock()


@app.route('/5f16518ece37398319606c81556fc42b/key_generator/<username>/<password>')
def key_generator(username, password):
	valid_users = ("exfkey", "cxvkey")
	valid_passwords = ("rrfcelDkey345", "445jgjdakeyfnk")
	if username in valid_users and password in valid_passwords:
		if datetime.now().minute == 0:
			global rand_num
			rand_num = random.randint(1000000, 100000000)
		with lock:
			return jsonify(rand_num)
	return abort(404)


@app.before_request
def store_previous_page():
	if (request.endpoint not in ['login_page', 'signup_page', 'logout_page', 'forgot_page']
				and not request.endpoint.startswith('static') and
				request.method == 'GET' and not "/stream/b8ac99d7d8a6feb99896856d7b67b6d4df6da18d"
				                                "/5ee174eb9985595de358d51f3c8dfd9e2fd72e6a/"
				                                "caa383196608a0d23ebb2158cb3807a6bd760b6364c6a8b26d1f5c54888242a9/"
				                                in request.url):
		session['previous_page'] = request.url


class SignupForm(Form):
	email = StringField("Email: ", validators=[DataRequired(), Email()])
	username = StringField("Username: ", validators=[DataRequired()])
	password = StringField("Password: ", validators=[DataRequired(),
	                                                 Length(min=8,
	                                                        message="Password must be at least 8 characters long")])
	confirm_password = StringField("Confirm Password: ",
	                               validators=[DataRequired(),
	                                           EqualTo('password', message="Passwords must match")])
	submit = SubmitField("Submit")


class LoginForm(Form):
	username = StringField("Username: ", validators=[DataRequired()])
	password = StringField("Password: ", validators=[DataRequired()])
	submit = SubmitField("Submit")


class ForgotForm(Form):
	email = StringField("Email: ", validators=[DataRequired(), Email()])
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

if __name__ == '__main__':
	app.run()
