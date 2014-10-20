from termcolor import colored
import requests
from requests.models import Request
import logging
import os


def configure_logging(level_env_var, time_env_var):
    if int(os.environ.get(time_env_var, "1")):
        format_str = '%(asctime)s '
    else:
        format_str = ''
    format_str += '%(levelname)5s ' + colored('[%(module)s.%(funcName)s] ', 'green')
    format_str += '%(message)s'

    logging.basicConfig(format=format_str,
            level=os.environ.get(level_env_var, 'INFO').upper())

def log_request(target, kind):
    def wrapper(*args, **kwargs):
        logger = kwargs.get('logger', logging.getLogger(__name__))
        if 'logger' in kwargs:
            del kwargs['logger']

        response = target(*args, **kwargs)

        r = Request(kind.upper(), *args, **kwargs)
        logger.info("%s from %s  %s", response.status_code, kind.upper(), r.url)
        for name in ['params', 'headers', 'data']:
            if getattr(r, name):
                logger.debug("    %s%s: %s", name[0].upper(), name[1:],
                        getattr(r, name))

        return response
    return wrapper

class LoggedRequest(object):
    def __getattr__(self, name):
        return log_request(getattr(requests, name), name)
logged_request = LoggedRequest()
