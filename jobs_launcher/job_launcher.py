import subprocess
import multiprocessing
import psutil
import time
import ctypes
# TODO: undo delay in monitor


def _late_kill(pid, delay, real_rc=None):
    proc = psutil.Process(pid)
    try:
        proc.wait(delay)
    except psutil.TimeoutExpired as err:
        if real_rc:
            real_rc.value = -1024
        for child in reversed(proc.children(recursive=True)):
            child.terminate()
        proc.terminate()


def launch_job(cmd_line):
    report = {'reportlink': '', 'total': 0, 'passed': 0, 'failed': 0, 'skipped': 1, 'duration': 0}

    started = time.time()

    child = subprocess.Popen(cmd_line, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)

    real_rc = multiprocessing.Value('i', 0)
    monitor = multiprocessing.Process(target=_late_kill, args=(child.pid, 600, real_rc))
    monitor.start()

    sub_skip = 0

    while True:
        output = child.stdout.readline()
        if output == b'' and child.poll() != None:
            break
        if output != b'' and output != b'\r\n':
            # TODO: exists decode problems with embed python
            output = output.decode("UTF-8")
            output_noeol = str(output).replace('\r', '')
            output_noeol = str(output_noeol).replace('\n', '')
            print(output_noeol)
            if "not recognized as an internal or external command" in output_noeol:
                sub_skip = 1
            if "The system cannot find the path specified" in output_noeol:
                sub_skip = 1

    rc = ctypes.c_long(child.poll()).value

    monitor.terminate()
    proc_time = int(time.time() - started)

    if real_rc.value != 0:
        rc = real_rc.value

    report['duration'] = proc_time

    if sub_skip or rc == 2:
        report['skipped'] = 1
    elif rc == 0:
        report['passed'] = 1
        report['skipped'] = 0
    else:
        report['failed'] = 1
        report['skipped'] = 0

    return report
