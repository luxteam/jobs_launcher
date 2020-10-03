import os
import json
import time
import argparse
from image_service_client import ISClient

res = []
transferred_test_cases = []

is_client = None
try:
    is_client = ISClient(
        url=os.getenv("IS_URL"),
        login=os.getenv("IS_LOGIN"),
        password=os.getenv("IS_PASSWORD")
    )
except Exception as e:
    print("Can't create Image Service")


def check_results(test_cases_path, session_dir):
    with open(test_cases_path) as f:
        global transferred_test_cases
        test_cases = json.loads(f.read())
        new_test_cases = {tc['case']: tc['status'] for tc in test_cases if tc['status'] in ('skipped', 'error', 'done') and not tc['case'] in transferred_test_cases}


        for test_case in new_test_cases:
            image_id = is_client.send_image(os.path.realpath(os.path.join(session_dir, test_case['render_color_path']))) if is_client else -1
            with open(os.path.realpath(os.path.join('..', session_dir, test_case['name'] + '_RPR.json'))) as f:
                report = json.loads(f.read())
            
            report['image_service_id'] = image_id
            with open(os.path.realpath(os.path.join('..', session_dir, test_case['name'] + '_RPR.json'))) as f:
                json.dump(f, report)

            # TODO: sending artefacts
            print('Senfing artefacts & images for: {}'.format(test_case))

        transferred_test_cases += list(new_test_cases.keys())
        diff = len(test_cases) - len(transferred_test_cases)
        print('Monitor is waiting {} cases'.format(diff))
        if not diff:
            return True

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--interval', required=False, default=5, type=int, help="time interval")
    parser.add_argument('--progress_file', required=True, type=str, help='progress file')
    parser.add_argument('--session_dir', required=True, type=str, help='session dir')

    args = parser.parse_args()

    check = 1
    while True:
        print('Check number {}'.format(check))
        check += 1
        result = check_results(args.progress_file, args.image_folder)
        if result:
            break
        time.sleep(args.interval)
