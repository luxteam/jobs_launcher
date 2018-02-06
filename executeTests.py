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

import jobs_launcher.jobs_parser
import jobs_launcher.job_launcher

SCRIPTS = os.path.dirname(os.path.realpath(__file__))


def validate_cmd_execution(stage_name, stage_path):
    stage_report = stage_name + '.json'
    if os.path.exists(os.path.join(stage_path, stage_report)):
        try:
            with open(os.path.join(stage_path, stage_report)) as file:
                report = file.read()
                report = json.loads(report)
        except OSError as e:
            main_logger.error('Error during stage validation {}'.format(str(e)))
            return 'FAILED'

        return report[0]['status']


def parse_cmd_variables(tests_root, cmd_variables):
    config_devices = {}
    new_config = []
    try:
        with open(os.path.join(os.path.split(tests_root)[0], 'scripts', 'Devices.config.json'), 'r') as file:
            config_devices = file.read()
            config_devices = json.loads(config_devices)
    except Exception as e:
        main_logger.error('Error while parse cmd {}'.format(str(e)))

    for item in cmd_variables['RenderDevice'].split(','):
        # if its int index of device
        if item in config_devices.values():
            pass
        # else - get index by name from json file
        elif config_devices:
            new_config.append(config_devices[item])

    # TODO: add check that 'RenderDevice' is digit, if config.json doesn't exist

    if new_config:
        cmd_variables['RenderDevice'] = ','.join(new_config)

    temp = cmd_variables['RenderDevice'].split(',')
    temp.sort()
    cmd_variables['RenderDevice'] = ','.join(temp)

    return cmd_variables


def main():

    level = 0
    delim = ' '*level

    parser = argparse.ArgumentParser()
    parser.add_argument('--tests_root', required=True, metavar="<dir>", help="tests root dir")
    parser.add_argument('--work_root', required=True, metavar="<dir>", help="tests root dir")
    parser.add_argument('--work_dir', required=False, metavar="<dir>", help="tests root dir")
    parser.add_argument('--cmd_variables', required=False, nargs="*")
    parser.add_argument('--test_package', required=False, nargs="*")

    args = parser.parse_args()

    main_logger.info('Started with args: {}'.format(args))

    if args.cmd_variables:
        args.cmd_variables = {args.cmd_variables[i]: args.cmd_variables[i+1] for i in range(0, len(args.cmd_variables), 2)}
        args.cmd_variables = parse_cmd_variables(args.tests_root, args.cmd_variables)
    else:
        args.cmd_variables = {}

    args.tests_root = os.path.abspath(args.tests_root)

    tests_path = os.path.abspath(args.tests_root)
    work_path = os.path.abspath(args.work_root)
    if not args.work_dir:
        args.work_dir = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    work_path = os.path.join(work_path, args.work_dir)

    try:
        os.mkdir(work_path)
    except OSError as e:
        main_logger.error(str(e))

    machine_info = core.system_info.get_machine_info()

    # session_dir = os.path.join(work_path, machine_info.get("host"))
    session_dir = work_path

    print('Working folder  : ' + work_path)
    print('Tests folder    : ' + tests_path)

    main_logger.info('Working folder: {}'.format(work_path))
    main_logger.info('Tests folder: {}'.format(tests_path))

    for mi in machine_info.keys():
        print('{0: <16}: {1}'.format(mi, machine_info[mi]))

    try:
        if os.path.isdir(session_dir):
            shutil.rmtree(session_dir)
        os.makedirs(session_dir)
    except OSError as e:
        print(delim + str(e))
        main_logger.error(str(e))

    found_jobs = []
    report = AutoDict()
    report['failed_tests'] = []
    report['machine_info'] = machine_info
    report['guid'] = uuid.uuid1().__str__()

    jobs_launcher.jobs_parser.parse_folder(level, tests_path, '', session_dir, found_jobs, args.cmd_variables, package_filter=args.test_package)

    # core.reportExporter.save_json_report(found_jobs, session_dir, 'found_jobs.json')

    for found_job in found_jobs:
        main_logger.info('Started job: {}'.format(found_job[0]))

        print("Processing {}  {}/{}".format(found_job[0], found_jobs.index(found_job)+1, len(found_jobs)))
        report['results'][found_job[0]][' '.join(found_job[1])] = {'reportlink': '', 'result_path': '', 'total': 0, 'passed': 0, 'failed': 0, 'skipped': 0, 'duration': 0}
        temp_path = os.path.abspath(found_job[4][0].format(SessionDir=session_dir))

        for i in range(len(found_job[3])):
            # print("  Executing job: ", found_job[3][i].format(SessionDir=session_dir))
            print("  Executing job {}/{}".format(i+1, len(found_job[3])))
            report['results'][found_job[0]][' '.join(found_job[1])]['duration'] += jobs_launcher.job_launcher.launch_job(found_job[3][i].format(SessionDir=session_dir))['duration']
            report['results'][found_job[0]][' '.join(found_job[1])]['result_path'] = os.path.relpath(temp_path, session_dir)

            # read state from stage report to check correct complete previous job
            # we still continue work to get report
            if validate_cmd_execution(found_job[5][i], temp_path) == 'FAILED':
                report['results'][found_job[0]][' '.join(found_job[1])]['failed'] = 1
                main_logger.warning('Job FAILED')
            elif validate_cmd_execution(found_job[5][i], temp_path) == 'TERMINATED':
                report['results'][found_job[0]][' '.join(found_job[1])]['failed'] = 1
                main_logger.warning('Job was TERMINATED')
            else:
                if not report['results'][found_job[0]][' '.join(found_job[1])]['failed']:
                    report['results'][found_job[0]][' '.join(found_job[1])]['passed'] = 1

        log = []
        for stage_report in found_job[5]:
            temp_report = os.path.join(temp_path, stage_report+'.json')
            if os.path.isfile(temp_report):
                with open(temp_report, 'r') as file:
                    log.append(json.loads(file.read()))

        report['results'][found_job[0]][' '.join(found_job[1])].update({'log': log})

    # json_report = json.dumps(report, indent = 4)
    # print(json_report)

    print("Saving session report")
    core.reportExporter.build_session_report(report, session_dir)
    main_logger.info('Saved session report')
    print("Saving summary report")
    core.reportExporter.build_summary_report(args.work_root)
    main_logger.info('Saved summary report')


if __name__ == "__main__":
    if not main():
        exit(0)
