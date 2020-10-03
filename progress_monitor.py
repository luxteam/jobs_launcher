import json
import time
import argparse


transferred_test_cases = []
def check_results(test_cases_path):
    with open(test_cases_path) as f:
        global transferred_test_cases
        test_cases = json.loads(f.read())
        new_test_cases = {tc['case']: tc['status'] for tc in test_cases if tc['status'] in ('skipped', 'error', 'done') and not tc['case'] in transferred_test_cases}

        # TODO: sending artefacts
        for test_case in new_test_cases: 
            print('Senfing artefacts & images for: {}'.format(test_case))

        transferred_test_cases += list(new_test_cases.keys())
        diff = len(test_cases) - len(transferred_test_cases)
        print('Monitor is waiting {} cases'.format(diff))
        if not diff:
            return True

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--interval', required=False, default=5, type=int, help="time interval")
    parser.add_argument('--progress_file', required=True, type=str ,help='progress file')

    args = parser.parse_args()

    check = 1
    while True:
        print('Check number {}'.format(check))
        check += 1
        result = check_results(args.progress_file)
        if result:
            break
        time.sleep(args.interval)
