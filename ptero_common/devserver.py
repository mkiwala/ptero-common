import errno
import os
import sys
import psutil
import signal
import time

honcho_process = None
child_pids = set()


# This is from a stackoverflow answer:
# http://stackoverflow.com/questions/600268/mkdir-p-functionality-in-python
def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def service_command_line(procfile_path, workers):
    return [
        'honcho', 'start', '-f', procfile_path, '-c',
        ','.join(["%s=%d" % (key, value) for key, value in workers.items()])]


def shutdown():
    if signal_processes(child_pids, signal.SIGINT):
        time.sleep(3)
        signal_processes(child_pids, signal.SIGKILL)


def signal_processes(pids, sig):
    signaled = []
    for p in pids:
        try:
            process = psutil.Process(p)
            process.send_signal(sig)
            signaled.append(process.pid)
        except psutil.NoSuchProcess:
            pass

    if len(signaled) > 0:
        sys.stderr.write(
            "Sent signal (%s) to processes: %s\n" % (sig, signaled))
        return True
    else:
        return False


def expand_children():
    for p in child_pids.copy():
        try:
            process = psutil.Process(p)
            child_pids.update(
                [p.pid for p in process.get_children(recursive=True)])
        except psutil.NoSuchProcess:
            pass


def cleanup():
    sys.stderr.write('Shutting down the devserver.\n')
    expand_children()
    try:
        honcho_process.send_signal(signal.SIGINT)
    except psutil.NoSuchProcess:
        return

    try:
        honcho_process.wait(timeout=3)
    except psutil.TimeoutExpired:
        pass

    shutdown()


def log_and_cleanup(signum, frame):
    sys.stderr.write("RECEIVED SIGNAL: '%s'\n" % signum)
    cleanup()


def setup_signal_handlers():
    signal.signal(signal.SIGINT, log_and_cleanup)
    signal.signal(signal.SIGTERM, log_and_cleanup)


def run(logdir, procfile_path, workers):
    global honcho_process

    setup_signal_handlers()

    if (logdir == '-'):
        outlog = sys.stdout
        errlog = sys.stderr
    else:
        mkdir_p(logdir)
        sys.stderr.write('Launching the devserver... logging to: %s\n' % logdir)
        outlog = open(os.path.join(logdir, 'honcho.out'), 'w')
        errlog = open(os.path.join(logdir, 'honcho.err'), 'w')

    honcho_process = psutil.Popen(
        service_command_line(procfile_path, workers), shell=False,
        stdout=outlog, stderr=errlog)
    time.sleep(3)
    sys.stderr.write('The devserver is now up.\n')
    child_pids.update(
        [p.pid for p in psutil.Process().get_children(recursive=True)])

    honcho_process.wait()
    cleanup()
