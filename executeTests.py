import argparse
import datetime
import os
import shutil
import webbrowser
import json
# TODO: do smth with testExecutor.core etc
import core.reportExporter
import core.system_info

import jobs_launcher.jobs_parser
import jobs_launcher.job_launcher

from core.auto_dict import AutoDict

SCRIPTS = os.path.dirname( os.path.realpath(__file__) )
# TODO: mb make common simpleRender for Maya and Max

def validate_cmd_execution(stage_name, stage_path):
    stage_report = stage_name + '.json'
    if os.path.exists(os.path.join(stage_path, stage_report)):
        with open(os.path.join(stage_path, stage_report)) as file:
            report = file.read()
            report = json.loads(report)
        return report[0]['status']


def main():
    level = 0
    delim = ' '*level

    parser = argparse.ArgumentParser()
    parser.add_argument('--tests_root', required=True, metavar="<dir>", help="tests root dir")
    parser.add_argument('--work_root', required=True, metavar="<dir>", help="tests root dir")
    parser.add_argument('--work_dir', required=False, metavar="<dir>", help="tests root dir")
    parser.add_argument('--cmd_variables', required=True, nargs="*")

    args = parser.parse_args()
    args.cmd_variables = {args.cmd_variables[i]: args.cmd_variables[i+1] for i in range(0, len(args.cmd_variables), 2)}
    print(args)

    tests_path = os.path.abspath(args.tests_root)
    work_path = os.path.abspath(args.work_root)
    if not args.work_dir:
        args.work_dir = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    work_path = os.path.join(work_path, args.work_dir)

    try:
        os.mkdir(work_path)
    except:
        pass

    machine_info = core.system_info.get_machine_info()

    session_dir = os.path.join(work_path, machine_info.get("host"))

    print('Working folder  : ' + work_path)
    print('Tests folder    : ' + tests_path)

    for mi in machine_info.keys():
        print('{0: <16}: {1}'.format(mi, machine_info[mi]))

    try:
        if os.path.isdir(session_dir):
            shutil.rmtree(session_dir)
        os.mkdir(session_dir)
    except OSError as e:
        print(delim + str(e))
        pass

    found_jobs = []
    report = AutoDict()
    report['failed_tests'] = []
    report['machine_info'] = machine_info

    jobs_launcher.jobs_parser.parse_folder(level, tests_path, '', session_dir, found_jobs, args.cmd_variables)

    # with open('d:\works.json', 'w') as file:
    #     json_jobs = json.dumps(found_jobs, indent = 4)
    #     json.dump(found_jobs, file, indent=' ')
    #     print("JSON JOBS", json_jobs)

    for found_job in found_jobs:
        # TODO: rewrite
        print("Processing ", found_job[0])
        report['results'][found_job[0]][' '.join(found_job[1])] = {'reportlink': '', 'total': 0, 'passed': 0, 'failed': 0, 'skipped': 1, 'duration': 0}
        temp_path = os.path.abspath(found_job[4][0].format(SessionDir=session_dir))

        # report['results'][found_job[0]][' '.join(found_job[1])] = jobs_launcher.job_launcher.launch_job(found_job[3][0].format(SessionDir=session_dir))

        for i in range(len(found_job[3])):
            print("  Executing job: ", found_job[3][i].format(SessionDir=session_dir))
            report['results'][found_job[0]][' '.join(found_job[1])]['duration'] += jobs_launcher.job_launcher.launch_job(found_job[3][i].format(SessionDir=session_dir))['duration']

            # report['results'][found_job[0]][' '.join(found_job[1])]['reportlink'] = os.path.join(temp_path, 'result.html')
            report['results'][found_job[0]][' '.join(found_job[1])]['reportlink'] = os.path.relpath(os.path.join(temp_path, 'result.html'), session_dir)

            # if not validate_cmd_execution(found_job[5][i], temp_path):
            if validate_cmd_execution(found_job[5][i], temp_path) == 'FAILED':
                report['results'][found_job[0]][' '.join(found_job[1])]['total'] = 1
                report['results'][found_job[0]][' '.join(found_job[1])]['failed'] = 1
                report['results'][found_job[0]][' '.join(found_job[1])]['passed'] = 0
                report['results'][found_job[0]][' '.join(found_job[1])]['skipped'] = 0
                break
            elif validate_cmd_execution(found_job[5][i], temp_path) == 'TERMINATED':
                report['results'][found_job[0]][' '.join(found_job[1])]['total'] = 1
                report['results'][found_job[0]][' '.join(found_job[1])]['failed'] = 1
                report['results'][found_job[0]][' '.join(found_job[1])]['passed'] = 0
                report['results'][found_job[0]][' '.join(found_job[1])]['skipped'] = 0
            else:
                report['results'][found_job[0]][' '.join(found_job[1])]['total'] = 1
                report['results'][found_job[0]][' '.join(found_job[1])]['skipped'] = 0
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
    # print("Saving summary report")
    # core.reportExporter.build_summary_report(work_path)
    # print("Sending report to server (now just copy to c:/reports_storage")

    # core.reportExporter.build_export_reports('c:/reports_storage/app/packages', 'RPR_Maya_Plugin', '2.2.3.3', session_dir)
    # core.reportExporter.build_export_reports('c:/reports_storage/app/packages', 'RPR_Max_Plugin', '2.1.3.3', session_dir)

    # webbrowser.get("C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s").\
    #     open(os.path.join(work_path, 'summary_report.html'))


if __name__ == "__main__":
    if not main():
        exit(0)
