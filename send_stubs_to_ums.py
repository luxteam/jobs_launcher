import os
import argparse
from core.config import *
import json
from ums_client import create_ums_client
from core.countLostTests import PLATFORM_CONVERTATIONS


ums_client_prod = create_ums_client("PROD")
ums_client_dev = create_ums_client("DEV")


def generate_stubs(cases_names, status):
    cases = []
    try:
        for case_name in cases_names:
            cases.append({
                "name": case_name,
                "status": status,
                "metrics": {
                    "render_time": -0.0
                },
                "artefacts": {
                    "rendered_image": status
                },
            })
    except:
        main_logger.error("Failed to generate stubs. Exception: {}".format(str(e)))
        main_logger.error("Traceback: {}".format(traceback.format_exc()))
    return cases


def send_stubs(suite, cases_names, status, env):
    cases = generate_stubs(cases_names, status)
    try:
        if ums_client_prod:
            ums_client_prod.get_suite_id_by_name(suite_name)
            send_try = 0
            while send_try < MAX_UMS_SEND_RETRIES:
                response_prod = ums_client_prod.send_test_suite(res=cases, env=env)
                main_logger.info('Test suite results sent to UMS PROD with code {} (try #{})'.format(response_prod.status_code, send_try))
                main_logger.info('Response from UMS PROD: \n{}'.format(response_prod.content))
                if response_prod and response_prod.status_code < 300:
                    response_data = json.loads(response_prod.content.decode("utf-8"))
                    if 'data' in response_data and 'test_suite_result_id' in response_data['data']:
                        test_suite_result_id_prod = response_data['data']['test_suite_result_id']
                    break
                send_try += 1
                time.sleep(UMS_SEND_RETRY_INTERVAL)
    except:
        main_logger.error("Failed to send stubs to UMS PROD. Exception: {}".format(str(e)))
        main_logger.error("Traceback: {}".format(traceback.format_exc()))

    try:
        if ums_client_dev:
            ums_client_dev.get_suite_id_by_name(suite_name)
            send_try = 0
            while send_try < MAX_UMS_SEND_RETRIES:
                response_dev = ums_client_dev.send_test_suite(res=cases, env=env)
                main_logger.info('Test suite results sent to UMS DEV with code {} (try #{})'.format(response_dev.status_code, send_try))
                main_logger.info('Response from UMS DEV: \n{}'.format(response_dev.content))
                if response_dev and response_dev.status_code < 300:
                    response_data = json.loads(response_dev.content.decode("utf-8"))
                    if 'data' in response_data and 'test_suite_result_id' in response_data['data']:
                        test_suite_result_id_dev = response_data['data']['test_suite_result_id']
                    break
                send_try += 1
                time.sleep(UMS_SEND_RETRY_INTERVAL)
    except:
        main_logger.error("Failed to send stubs to UMS DEV. Exception: {}".format(str(e)))
        main_logger.error("Traceback: {}".format(traceback.format_exc()))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--path_to_skipped_cases", type=str, metavar="<path>", help="path to json with skipped cases")
    parser.add_argument("--path_to_error_cases", type=str, metavar="<path>", help="path to json with error cases")
    parser.add_argument("--host", required=True, type=str, help="name of host")
    parser.add_argument("--os", required=True, type=str, help="name of os")
    parser.add_argument("--gpu", required=True, type=str, help="name of gpu")

    args = parser.parse_args()

    data_summary = []
    env = {}

    try:
        env = {'host': args.host, 'os': PLATFORM_CONVERTATIONS[args.os]["os_name"], 'gpu': PLATFORM_CONVERTATIONS[args.os]["cards"][args.gpu]}
        if ums_client_prod:
            ums_client_prod.define_environment(env)
        if ums_client_dev:
            ums_client_dev.define_environment(env)
    except:
        main_logger.error("Failed to define environment. Exception: {}".format(str(e)))
        main_logger.error("Traceback: {}".format(traceback.format_exc()))

    try:
        if args.path_to_skipped_cases:
            with open(args.path_to_skipped_cases, "r") as file:
                skipped_cases_data = json.load(file)
                data_summary.append({'status': 'skipped', 'data': skipped_cases_data})
    except:
        main_logger.error("Failed to read list of skipped cases. Exception: {}".format(str(e)))
        main_logger.error("Traceback: {}".format(traceback.format_exc()))
    try:
        if args.path_to_error_cases:
            with open(args.path_to_error_cases, "r") as file:
                error_cases_data = json.load(file)
                data_summary.append({'status': 'error', 'data': error_cases_data})
    except:
        main_logger.error("Failed to read list of error cases. Exception: {}".format(str(e)))
        main_logger.error("Traceback: {}".format(traceback.format_exc()))

    for data in data_summary:
        for platform in data['data']:
            for suite in data['data'][platform]:
                send_stubs(suite, data['data'][platform][suite], data['status'], env)
