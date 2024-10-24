import flask
from flask import render_template
from flask.views import MethodView
app = flask.Flask(__name__)

class MainPage(MethodView):
	def get(self):
		return render_template("index.html")

class SignUpPage(MethodView):
	def get(self):
		return render_template("signup.html")

class LoginPage(MethodView):
	def get(self):
		return render_template("login.html")

class MobileAppPage(MethodView):
	def get(self):
		return render_template("mobile_app.html")

class SecurityCameraPage(MethodView):
	def get(self):
		return render_template("security_camera.html")

app.add_url_rule('/', view_func=MainPage.as_view('main_page'))
app.add_url_rule('/signup', view_func=SignUpPage.as_view('signup_page'))
app.add_url_rule('/login', view_func=LoginPage.as_view('login_page'))
app.add_url_rule('/mobile-app', view_func=MobileAppPage.as_view('mobile_app_page'))
app.add_url_rule('/security-camera', view_func=SecurityCameraPage.as_view('security_camera_page'))
if __name__ == '__main__':
	app.run(debug=True)