import json
import requests
import argparse
import subprocess
from core.system_info import get_machine_info


# RBS_DEV = "https://rbsdbdev.cis.luxoft.com"
# RBS = "https://rbsdb.cis.luxoft.com"
TEST = "http://localhost:5000"
links = [TEST]


def get_gpu():
	try:
		s = subprocess.Popen("wmic path win32_VideoController get name", stdout=subprocess.PIPE)
		stdout = s.communicate()
		render_device = stdout[0].decode("utf-8").split('\n')[1].replace('\r', '').strip(' ')
		return render_device
	except:
		pass


def get_headers(link):
	r = requests.post(link + "/api/login", auth=requests.auth.HTTPBasicAuth('root', 'root'))
	print(r)
	return {"Authorization": "Bearer " + json.loads(r.content)['token']}


def main():
	parser = argparse.ArgumentParser()

	parser.add_argument('--tool', required=True)
	parser.add_argument('--branch', required=True)
	parser.add_argument('--build', required=True)
	parser.add_argument('--test_groups', required=True)
	
	args = parser.parse_args()
	args.test_groups = args.test_groups.split(",")

	template = {
		"build_name": args.build,
		"branch": args.branch,
		"tool": args.tool,
		"groups": args.test_groups,
	}

	machine_info = get_machine_info()
	machine_info["render_device"] = get_gpu()
	template["tester_info"] = machine_info

	with open("machine_info.json", "w") as file:
		json.dump(template, file, indent=4)

	with open("machine_info.json", "rb") as file:
		files = {"data": file.read()}

	for link in links:
		headers = get_headers(link)
		r = requests.post(link + "/report/setTester", files=files, headers=headers)

if __name__ == "__main__":
	main()
