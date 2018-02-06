import subprocess
import psutil
import time
import core.config


def launch_job(cmd_line):
    report = {'total': 0, 'passed': 0, 'failed': 0, 'skipped': 1, 'duration': 0}
    core.config.main_logger.info('Started job: {}'.format(cmd_line))
    started = time.time()

    p = psutil.Popen(cmd_line, stdout=subprocess.PIPE, shell=True)
    try:
        rc = p.wait(timeout=core.config.TIMEOUT)
    except psutil.TimeoutExpired as err:
        rc = 1
        for child in reversed(p.children(recursive=True)):
            child.terminate()
        p.terminate()

    proc_time = int(time.time() - started)

    report['duration'] = proc_time

    if rc == 0:
        core.config.main_logger.info('Job was completed normal')
        report['passed'] = 1
        report['skipped'] = 0
    else:
        core.config.main_logger.warning('Job was terminated by timeout')
        report['failed'] = 1
        report['skipped'] = 0

    return report
