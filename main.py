from db_functions import add_user, user_exists, create_table, verify_password, verify_email
from flask import render_template, request, Flask, session
from flask.views import MethodView
from wtforms import Form, StringField, IntegerField, BooleanField
from wtforms.fields.simple import SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from sendemailpy3 import send_gmail
import os
import sqlite3

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config["SESSION_TYPE"] = "memcache"

connection = create_table()


class MainPage(MethodView):
	def get(self):
		return render_template("index.html")


class SignUpPage(MethodView):
	def get(self):
		signup_form = SignupForm()
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
			else:
				error_code = "Passwords do not match"
		else:
			error_code = "Username already exists"
		return render_template("signup.html", signup_form=signup_form, error_code=error_code)


class LoginPage(MethodView):
	def get(self):
		login_form = LoginForm()
		return render_template("login.html", login_form=login_form)

	def post(self):
		login_form = LoginForm(request.form)
		username = str(login_form.username.data)
		password = str(login_form.password.data)
		error_code = "Successfully logged in"
		if verify_password(username, password):
			session['logged_in'] = True
			session['username'] = username
		else:
			error_code = "Invalid username or password"
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
if __name__ == '__main__':
	app.run(debug=True)
