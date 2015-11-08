from pip.commands.freeze import freeze
import datetime
import os
import psutil
import subprocess


def get_server_info(celery_app_import_path):
    p = psutil.Process()
    started = datetime.datetime.fromtimestamp(p.create_time())
    uptime = str(datetime.datetime.now() - started)
    started_str = started.strftime("%Y-%m-%d %H:%M:%S")

    installed_modules = [l for l in freeze()]

    celery_status = subprocess.check_output(['celery', '-A',
        celery_app_import_path, '--no-color', '--timeout=1', 'status'])
    celery_status_list = [s for s in celery_status.split('\n') if len(s)]

    if 'GIT_SHA' in os.environ:
        git_sha = os.environ['GIT_SHA']
    else:
        git_sha = 'Unknown'

    return {
            'celeryStatus': celery_status_list,
            'gitSha': git_sha,
            'installedModules': installed_modules,
            'startedAt': started_str,
            'uptime': uptime,
            }
