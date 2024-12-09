import requests
import datetime

with open("device_id.txt", "r") as f:
	info = f.readlines()
	device = info[0]

time = datetime.datetime.now().minute
DB_URL = ("https://vigilancesolutions.pythonanywhere.com/478cb55db6df5b5b4f9d38e081161edf"
          "/3ec984b8ebcb95979aafc140ab3175f7/afb3132ee624f40beae950c57ae0f3a5/5f16518ece37398319606c81556fc42b")
KEY = str(requests.get("https://vigilancesolutions.pythonanywhere.com/5f16518ece37398319606c81556fc42b/key_generator/"
                          "exfkey/445jgjdakeyfnk").json())

headers = {
	'X-Metadata-Key': KEY
}


response = requests.post(DB_URL, headers=headers)
print(response.text)
if response.status_code == 200:
	for username, email, devices in response.json():
		if device in str(devices):
			with open("device_id.txt", "a") as f:
				f.write(f"{username}\n")
			with open("emails.txt", "w") as f:
				f.write(f"{email}\n")
