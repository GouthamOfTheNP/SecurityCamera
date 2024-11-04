from flask import Flask, request, render_template
import cv2
import numpy as np

app = Flask(__name__)
user_frames = {}

@app.route('/')
def index():
	return "Home Page", 200

@app.route('/upload_frame', methods=['POST'])
def upload_frame():
	user_id = request.form.get('user_id')
	print(user_id)
	if 'frame' not in request.files:
		return "No frame found", 400

	# Read the frame from the request
	frame = request.files['frame'].read()

	# Convert the byte data to a numpy array and decode it to an image
	np_frame = np.frombuffer(frame, np.uint8)
	image = cv2.imdecode(np_frame, cv2.IMREAD_COLOR)

	# Store the latest frame for the user
	if user_id:
		user_frames[user_id] = image

	return "Frame received", 200


@app.route('/stream/<user_id>')
def stream(user_id):
	if user_id in user_frames:
		print(user_frames)
		_, buffer = cv2.imencode('.jpg', user_frames[user_id])
		return render_template('server.html', user_id=user_id)
	return "User not found", 404


@app.route('/stream_default')
def stream_default():
	if user_frames:
		first_user_id = next(iter(user_frames))
		_, buffer = cv2.imencode('.jpg', user_frames[first_user_id])
		return buffer.tobytes(), 200, {'Content-Type': 'image/jpeg'}
	return "No frames available", 404

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5000)