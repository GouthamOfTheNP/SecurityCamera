import zipfile
import os
import cv2
import time
import sendemailpy3 as smpy
from threading import Thread
from datetime import datetime

with open("emails.txt", "r") as file:
	receiver_email = [email.strip() for email in file.readlines()]


def create_video(video_frames, video_name):
	height, width, layers = video_frames[0].shape
	fourcc = cv2.VideoWriter_fourcc(*'mp4v')
	fps = 15
	out = cv2.VideoWriter(video_name, fourcc, fps, (width, height))

	for frame in video_frames:
		out.write(frame)

	out.release()


def merge_videos(video_files, output_name):
	cap = cv2.VideoCapture(video_files[0])
	frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
	frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
	fps = cap.get(cv2.CAP_PROP_FPS)
	cap.release()

	fourcc = cv2.VideoWriter_fourcc(*'mp4v')
	out = cv2.VideoWriter(output_name, fourcc, fps, (frame_width, frame_height))

	for video in video_files:
		cap = cv2.VideoCapture(video)
		while True:
			ret, frame = cap.read()
			if not ret:
				break
			out.write(frame)
		cap.release()

	out.release()
	print(f"Videos merged into: {output_name}")


def zip_video_file(video_file):
	zip_file_name = f"{os.path.splitext(video_file)[0]}.zip"  # Create a ZIP file name based on the video file name
	with zipfile.ZipFile(zip_file_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
		zipf.write(video_file, os.path.basename(video_file))  # Add the video file to the ZIP archive
	return zip_file_name


def send_message(emails):
	sender_email = "noreplysmtpimportant@gmail.com"
	sender_password = "yqfd dnzf oyqe hvph"

	subject = "Intruder detected at your camera's location!"
	body = "Download the following videos to see what happened at what time."

	if video_records_detected:
		for record in video_records_detected:
			zipped_record = zip_video_file(record)
			try:
				for email in emails:
					smpy.send_gmail(subject, body, email, sender_email, sender_password, filepath=zipped_record)
					print(f"Email sent to {email} with attachment: {zipped_record}")
			except Exception as e:
				print(f"Error sending email: {e}")


images = []
video_files = []
video_records = []
image_files_detected = []
video_records_detected = []

save_dir = "./footage/"
if not os.path.exists(save_dir):
	os.makedirs(save_dir)

iterations = 0
iterations2 = 0
image_time = 75
merge_time_multiplier = 12
merge_time = image_time * merge_time_multiplier

video = cv2.VideoCapture(0)
fps = int(video.get(cv2.CAP_PROP_FPS))
frames_per_video = 5 * fps
rectangle = None

first_frame = None

time.sleep(1)

while True:
	check, frame = video.read()
	gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	gray_frame_gaussian_blur = cv2.GaussianBlur(gray_frame, (21, 21), 0)
	cv2.imshow("Video", frame)

	if first_frame is None:
		first_frame = gray_frame_gaussian_blur

	delta_frame = cv2.absdiff(first_frame, gray_frame_gaussian_blur)
	thresh_frame = cv2.threshold(delta_frame, 60, 255, cv2.THRESH_BINARY)[1]
	dilated_frame = cv2.dilate(thresh_frame, None, iterations=2)
	contours, check = cv2.findContours(dilated_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

	for contour in contours:
		if cv2.contourArea(contour) < 10000:
			continue
		x, y, w, h = cv2.boundingRect(contour)
		rectangle = cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 3)

	cv2.imshow("Video", frame)
	key = cv2.waitKey(1)
	images.append(frame)

	if rectangle is not None and rectangle.any():
		image_name = os.path.join(save_dir, f'time_stamp_image_detected{datetime.now()}.jpg')
		cv2.imwrite(image_name, frame)
		image_files_detected.append(image_name)
	if len(images) == frames_per_video:
		video_name = os.path.join(save_dir, f'time_stamp_{datetime.now()}.mp4')
		create_video(images, video_name)
		video_files.append(video_name)
		images = []

	if len(video_files) % 12 == 0 and len(video_files) != 0:
		merged_name = os.path.join(save_dir, f"merged_time_stamp_{datetime.now()}.mp4")
		merge_videos(video_files, merged_name)
		video_files = []
		video_records.append(merged_name)

	if iterations % 150 == 0:
		if image_files_detected and len(image_files_detected) != 0:
			image_files_video_detected = []
			for f in image_files_detected:
				frame = cv2.imread(f)
				image_files_video_detected.append(frame)
			merged_name = os.path.join(save_dir, f"time_stamp_detected{datetime.now()}.mp4")
			create_video(image_files_video_detected, merged_name)
			video_records_detected.append(merged_name)
		email_thread = Thread(target=send_message, args=(receiver_email,))
		email_thread.daemon = True
		email_thread.start()
		video_records_detected = []

	iterations += 1

	if key == ord('q'):
		break

video.release()
cv2.destroyAllWindows()

if image_files_detected and len(image_files_detected) != 0:
	image_files_video_detected = []
	for f in image_files_detected:
		frame = cv2.imread(f)
		image_files_video_detected.append(frame)
	merged_name = os.path.join(save_dir, f"time_stamp_detected{datetime.now()}.mp4")
	create_video(image_files_video_detected, merged_name)
	video_records_detected.append(merged_name)

send_message(receiver_email)

