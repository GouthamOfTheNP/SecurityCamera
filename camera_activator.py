import requests

DB_URL = ("https://vigilancesolutions.pythonanywhere.com/478cb55db6df5b5b4f9d38e081161edf"
          "/3ec984b8ebcb95979aafc140ab3175f7/afb3132ee624f40beae950c57ae0f3a5/5f16518ece37398319606c81556fc42b")

with open("device_id.txt", "r") as f:
	info = f.readlines()
	device = info[0]

for username, devices in requests.get(DB_URL).json():
	if devices:
		with open("device_id.txt", "a") as f:
			f.write(f"{username}:\n")