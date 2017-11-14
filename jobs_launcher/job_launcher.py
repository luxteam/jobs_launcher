import subprocess
import psutil
import time


def launch_job(cmd_line):
    report = {'reportlink': '', 'total': 0, 'passed': 0, 'failed': 0, 'skipped': 1, 'duration': 0}

    started = time.time()

    p = psutil.Popen(cmd_line, stdout=subprocess.PIPE)
    rc = p.wait(timeout=2000)

    proc_time = int(time.time() - started)

    report['duration'] = proc_time

    if rc == 0:
        report['passed'] = 1
        report['skipped'] = 0
    else:
        report['failed'] = 1
        report['skipped'] = 0

    return report