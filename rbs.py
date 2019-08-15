import json
import argparse
import requests
from platform import system
import subprocess
from core.system_info import get_machine_info


RBS_DEV = "https://rbsdbdev.cis.luxoft.com"
RBS = "https://rbsdb.cis.luxoft.com"

links = [RBS_DEV, RBS]

gpu_map = {
	"AMD_WX7100": "AMD Radeon (TM) Pro WX 7100 Graphics",
	"AMD_WX9100": "Radeon (TM) Pro WX 9100",
	"AMD_RXVEGA": "Radeon RX Vega",
	"NVIDIA_GF1080TI": "GeForce GTX 1080 Ti",
	"RadeonPro560": "AMD Radeon Pro 560 (Metal)"
}


def get_gpu():
	os = system()
	if os == "Windows":
		try:
			s = subprocess.Popen("wmic path win32_VideoController get name", stdout=subprocess.PIPE)
			stdout = s.communicate()
			render_device = stdout[0].decode("utf-8").split('\n')[1].replace('\r', '').strip(' ')
			return {"render_device": render_device}
		except Exception as err:
			print("Render device not found - set from map.")
			return {"render_device": gpu_map[os.environ["GPU"].split(":")[1]]}
	else:
		return {"render_device": gpu_map[os.environ["GPU"].split(":")[1]]}

def get_headers(link, login, password):
	r = requests.post(link + "/api/login", auth=requests.auth.HTTPBasicAuth(login, password))
	return {"Authorization": "Bearer " + json.loads(r.content)['token']}


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('--tool', required=True)
	parser.add_argument('--branch',  required=True)
	parser.add_argument('--build', required=True)
	parser.add_argument('--tests', nargs='+', required=False, default=[])
	parser.add_argument('--tests_package', required=False)
	parser.add_argument('--login', required=True)
	parser.add_argument('--password', required=True)
	args = parser.parse_args()

	if args.tests:
		test_groups = args.tests
	elif args.tests_package:
		try:
			with open('../jobs/{0}'.format(args.tests_package)) as file:
				test_groups = [group.strip() for group in file.read().split('\n') if group]
		except Exception as err:
			return False
	else:
		return False

	data = {
		"build_name": args.build,
		"branch": args.branch,
		"tool": args.tool,
		"groups": test_groups,
		"tester_info": {**get_machine_info(), **get_gpu()}
	}

	print(data)

	for link in links:
		headers = get_headers(link, args.login, args.password)
		requests.post(
			link + "/report/setTester",
			params={'data': str(json.dumps(data))},
			headers=headers
		)


# >>> python rbs.py --tool Maya --branch weekly --build 1024 --test_groups <Group1> <Group2> <Group3> --password <password> --login <login>
if __name__ == "__main__":
	main()
