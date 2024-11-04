from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)


@app.route('/', methods=['GET'])
def home_page():
	return "Home page of user database. Please travel to the specified location to get access."




if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5000)  # Accessible on your local network
