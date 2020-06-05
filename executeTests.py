import argparse
import datetime
import os
import shutil
import json
import uuid

import core.reportExporter
import core.system_info
from core.auto_dict import AutoDict
from core.config import *
try:
    from local_config import *
except ImportError:
    main_logger.critical("local config file not found. Default values will be used.")
    main_logger.critical("Correct report building isn't guaranteed")
    from core.defaults_local_config import *


import jobs_launcher.jobs_parser
import jobs_launcher.job_launcher

from rbs_client import RBS_Client, str2bool
from rbs_client import logger as rbs_logger
from image_service_client import ISClient


SCRIPTS = os.path.dirname(os.path.realpath(__file__))


def parse_cmd_variables(tests_root, cmd_variables):
    # if TestsFilter doesn't exist or is empty - set it 'full'
    if 'TestsFilter' not in cmd_variables.keys() or not cmd_variables['TestsFilter']:
        cmd_variables.update({'TestsFilter': 'full'})

    return cmd_variables


def main():

    # create RBS client
    rbs_client = None
    use_rbs = None
    try:
        use_rbs = str2bool(os.getenv('RBS_USE'))
    except Exception as e:
        print('Exception when getenv RBS USE: {}'.format(str(e)))
    if use_rbs:
        try:
            rbs_client = RBS_Client(
                job_id = os.getenv("RBS_JOB_ID"),
                url = os.getenv("RBS_URL"),
                build_id = os.getenv("RBS_BUILD_ID"),
                env_label = os.getenv("RBS_ENV_LABEL"),
                suite_id = None)
            print("RBS Client created")
        except Exception as e:
            print("RBS Client creation error: {}".format(e))

    level = 0
    delim = ' '*level

    parser = argparse.ArgumentParser()
    parser.add_argument('--tests_root', required=True, metavar="<dir>", help="tests root dir")
    parser.add_argument('--work_root', required=True, metavar="<dir>", help="tests root dir")
    parser.add_argument('--work_dir', required=False, metavar="<dir>", help="tests root dir")
    parser.add_argument('--cmd_variables', required=False, nargs="*")
    parser.add_argument('--test_filter', required=False, nargs="*", default=[])
    parser.add_argument('--package_filter', required=False, nargs="*", default=[])
    parser.add_argument('--file_filter', required=False)
    parser.add_argument('--execute_stages', required=False, nargs="*", default=[])

    args = parser.parse_args()

    main_logger.info('Started with args: {}'.format(args))

    if args.cmd_variables:
        args.cmd_variables = {
            args.cmd_variables[i]: args.cmd_variables[i+1] for i in range(0, len(args.cmd_variables), 2)
        }
        args.cmd_variables = parse_cmd_variables(args.tests_root, args.cmd_variables)
    else:
        args.cmd_variables = {}

    args.cmd_variables['TestCases'] = None

    args.tests_root = os.path.abspath(args.tests_root)

    main_logger.info('Args parsed to: {}'.format(args))

    tests_path = os.path.abspath(args.tests_root)
    work_path = os.path.abspath(args.work_root)

    if not args.work_dir:
        args.work_dir = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    work_path = os.path.join(work_path, args.work_dir)

    if not os.path.exists(work_path):
        try:
            os.makedirs(work_path)
        except OSError as e:
            main_logger.error(str(e))

    # session_dir = os.path.join(work_path, machine_info.get("host"))
    session_dir = work_path

    if '' in args.test_filter:
        args.test_filter = []

    if '' in args.package_filter:
        args.package_filter = []

    # extend test_filter by values in file_filter
    if args.file_filter and args.file_filter != 'none':
        try:
            with open(os.path.join(args.tests_root, args.file_filter), 'r') as file:
                if args.file_filter.endswith('json'):
                    args.cmd_variables['TestCases'] = os.path.abspath(os.path.join(args.tests_root, args.file_filter))
                    args.test_filter.extend([x for x in json.loads(file.read()).keys()])
                else:
                    args.test_filter.extend(file.read().splitlines())
        except Exception as e:
            main_logger.error(str(e))

    print('Working folder  : ' + work_path)
    print('Tests folder    : ' + tests_path)

    main_logger.info('Working folder: {}'.format(work_path))
    main_logger.info('Tests folder: {}'.format(tests_path))

    machine_info = core.system_info.get_machine_info()
    for mi in machine_info.keys():
        print('{0: <16}: {1}'.format(mi, machine_info[mi]))


    # send machine info to rbs
    if rbs_client:
        print('Tests filter: ' + str(args.test_filter))
        for group in args.test_filter:
            group = group.replace(' ', '').replace(",", '').replace('"', '').replace('[', '').replace(']', '')
            rbs_client.get_suite_id_by_name(group)
            # send machine info to rbs
            env = {"gpu": core.system_info.get_gpu(), **machine_info}
            env.pop('os')
            env.update({'hostname': env.pop('host'), 'cpu_count': int(env['cpu_count'])})
            rbs_client.define_environment(env)

    found_jobs = []
    report = AutoDict()
    report['failed_tests'] = []
    report['machine_info'] = machine_info
    report['guid'] = uuid.uuid1().__str__()

    try:
        if os.path.isdir(session_dir):
            shutil.rmtree(session_dir)
        os.makedirs(session_dir)
    except OSError as e:
        print(delim + str(e))
        main_logger.error(str(e))

    jobs_launcher.jobs_parser.parse_folder(level, tests_path, '', session_dir, found_jobs, args.cmd_variables,
                                           test_filter=args.test_filter, package_filter=args.package_filter)
    core.reportExporter.save_json_report(found_jobs, session_dir, 'found_jobs.json')

    for found_job in found_jobs:
        main_logger.info('Started job: {}'.format(found_job[0]))

        print("Processing {}  {}/{}".format(found_job[0], found_jobs.index(found_job)+1, len(found_jobs)))
        main_logger.info("Processing {}  {}/{}".format(found_job[0], found_jobs.index(found_job)+1, len(found_jobs)))
        report['results'][found_job[0]][' '.join(found_job[1])] = {
            'result_path': '', 'total': 0, 'passed': 0, 'failed': 0, 'error': 0, 'skipped': 0, 'duration': 0
        }
        temp_path = os.path.abspath(found_job[4][0].format(SessionDir=session_dir))

        for i in range(len(found_job[3])):
            if (args.execute_stages and str(i + 1) in args.execute_stages) or not args.execute_stages:
                print("  Executing job {}/{}".format(i+1, len(found_job[3])))
                main_logger.info("  Executing job {}/{}".format(i+1, len(found_job[3])))
                report['results'][found_job[0]][' '.join(found_job[1])]['duration'] += \
                    jobs_launcher.job_launcher.launch_job(found_job[3][i].format(SessionDir=session_dir), found_job[6][i])['duration']
            report['results'][found_job[0]][' '.join(found_job[1])]['result_path'] = os.path.relpath(temp_path, session_dir)
        main_logger.newline()

    # json_report = json.dumps(report, indent = 4)
    # print(json_report)

    print("Saving session report")
    core.reportExporter.build_session_report(report, session_dir)
    main_logger.info('Saved session report\n\n')
    shutil.copyfile('launcher.engine.log', os.path.join(session_dir, 'launcher.engine.log'))

    if rbs_client:
        print("Try to send results to RBS")
        is_client = None
        try:
            is_client = ISClient(os.getenv("IMAGE_SERVICE_URL"))
            print("Image Service client created")
        except Exception as e:
            print("Image Service client creation error: {}".format(str(e)))


        res = []
        try:
            print('Start preparing results')
            cases = []
            suites = []

            with open(os.path.join(session_dir, 'session_report.json')) as file:
                data = json.loads(file.read())
                suites = data["results"]

            for suite in suites:
                cases = suite[""]["render_results"]
                for case in cases:
                    image_id = is_client.send_image(os.path.realpath(os.path.join(session_dir, case['render_color_path']))) if is_client else -1
                    res.append({
                        'name': case['test_case'],
                        'status': case['test_status'],
                        'metrics': {
                            'render_time': case['render_time']
                        },
                        "artefacts": {
                            "rendered_image": str(image_id)
                        }
                    })

                rbs_client.get_suite_id_by_name(case['test_group'])
                # send machine info to rbs
                env = {"gpu": get_gpu(), **get_machine_info()}
                env.pop('os')
                env.update({'hostname': env.pop('host'), 'cpu_count': int(env['cpu_count'])})
                print(env)

                response = rbs_client.send_test_suite(res=res, env=env)
                print('Test suite results sent with code {}'.format(response.status_code))
                print(response.content)

        except Exception as e:
            print("Test case result creation error: {}".format(str(e)))



if __name__ == "__main__":
    if not main():
        exit(0)
