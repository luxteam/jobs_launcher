import os
import json
import time
import argparse
import hashlib

from image_service_client import ISClient
from ums_client import UMS_Client
from minio_client import UMS_Minio
from core.config import *

res = []
transferred_test_cases = []

is_client = None
ums_client = None
minio_client = None
try:
    is_client = ISClient(
        url=os.getenv("IS_URL"),
        login=os.getenv("IS_LOGIN"),
        password=os.getenv("IS_PASSWORD")
    )
except Exception as e:
    main_logger.error("Can't create Image Service client")
try:
    ums_client = UMS_Client(
        job_id=os.getenv("UMS_JOB_ID"),
        url=os.getenv("UMS_URL"),
        build_id=os.getenv("UMS_BUILD_ID"),
        env_label=os.getenv("UMS_ENV_LABEL"),
        suite_id=None,
        login=os.getenv("UMS_LOGIN"),
        password=os.getenv("UMS_PASSWORD")
    )
except Exception as e:
    main_logger.error("Can't create UMS client")
try:
    minio_client = UMS_Minio(
        product_id=ums_client.job_id,
        enpoint=os.getenv("MINIO_ENDPOINT"),
        access_key=os.getenv("MINIO_ACCESS_KEY"),
        secret_key=os.getenv("MINIO_SECRET_KEY")
    )
except Exception as e:
    main_logger.error("Can't create MINIO client")


def render_color_full_path(session_dir, suite_name, render_color_path):
    return os.path.realpath(os.path.join(session_dir, suite_name, render_color_path))


def get_cases_existence_info_by_hashes(session_dir, suite_name, test_cases):
    cases_hashes_info = {}
    cases_hashes = {}
    for case in test_cases:
        with open(os.path.join(session_dir, suite_name, case + '_RPR.json')) as case_file:
            case_file_data = json.load(case_file)[0]
            with open(render_color_full_path(session_dir, suite_name, case_file_data['render_color_path']), 'rb') as img:
                bytes_data = img.read()
                cases_hashes[case] = hashlib.md5(bytes_data).hexdigest()

    hash_info_from_is = is_client.get_existence_info_by_hash(
        [case_hash for case, case_hash in cases_hashes.items() if case_hash]
    )
    if hash_info_from_is:
        cases_hashes_info = {
            case: hash_info_from_is[case_hash]
            for case, case_hash in cases_hashes.items() if case_hash in hash_info_from_is
        }
    return cases_hashes_info


def check_results(session_dir, suite_name):
    test_cases_path = os.path.join(session_dir, suite_name, 'test_cases.json')
    ums_client.get_suite_id_by_name(suite_name)
    minio_client.upload_file(test_cases_path, ums_client.build_id, ums_client.suite_id)
    with open(test_cases_path) as test_cases_file:
        global transferred_test_cases
        test_cases = json.load(test_cases_file)
        new_test_cases = {tc['case']: tc['status'] for tc in test_cases if tc['status'] in ('skipped', 'error', 'done') and not tc['case'] in transferred_test_cases}

        new_cases_existence_hashes_info = get_cases_existence_info_by_hashes(session_dir, suite_name, new_test_cases)
        print('Got hashes info from image service:\n{}'.format(json.dumps(new_cases_existence_hashes_info, indent=2)))

        for test_case in new_test_cases:
            print('Sending artefacts & images for: {}'.format(test_case))
            with open(os.path.join(session_dir, suite_name, test_case + '_RPR.json')) as case_file:
                case_file_data = json.load(case_file)[0]

                if test_case in new_cases_existence_hashes_info and \
                        new_cases_existence_hashes_info[test_case] and \
                        'id' in new_cases_existence_hashes_info[test_case]:
                    print("Use id found by hash for case: {}".format(test_case))
                    image_id = new_cases_existence_hashes_info[test_case]['id']
                else:
                    print("Upload new image for case: {}".format(test_case))
                    image_id = is_client.send_image(render_color_full_path(session_dir, suite_name, case_file_data['render_color_path'])) if is_client else -1
                case_file_data['image_service_id'] = image_id

            with open(os.path.join(session_dir, suite_name, test_case + '_RPR.json'), 'w') as case_file:
                json.dump([case_file_data], case_file)

        transferred_test_cases += list(new_test_cases.keys())
        diff = len(test_cases) - len(transferred_test_cases)
        print('Monitor is waiting {} cases'.format(diff))
        if not diff:
            return True

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--interval', required=False, default=5, type=int, help="time interval")
    parser.add_argument('--session_dir', required=True, type=str, help='session dir')
    parser.add_argument('--suite_name', required=True, type=str, help='suite name')

    args = parser.parse_args()

    check = 1
    while True:
        print('Check number {}'.format(check))
        check += 1
        result = check_results(args.session_dir, args.suite_name)
        if result:
            break
        time.sleep(args.interval)
