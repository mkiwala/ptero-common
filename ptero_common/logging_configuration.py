from termcolor import colored
import requests
from requests.models import Request
import logging
import os

try:
    from flask import request
except:
    # Not everybody who uses ptero_common has requires/uses flask
    pass


def configure_celery_logging(service_name):
    configure_logging(
        'PTERO_%s_LOG_LEVEL' % service_name,
        'PTERO_%s_LOG_WITH_TIMESTAMPS' % service_name)
    logging.getLogger('requests').setLevel(
        os.environ.get('PTERO_%s_REQUESTS_LOG_LEVEL' % service_name, 'WARN'))
    logging.getLogger('celery').setLevel(
        os.environ.get('PTERO_%s_CELERY_LOG_LEVEL' % service_name, 'WARN'))
    logging.getLogger('amqp').setLevel(
        os.environ.get('PTERO_%s_AMQP_LOG_LEVEL' % service_name, 'WARN'))
    logging.getLogger('kombu').setLevel(
        os.environ.get('PTERO_%s_KOMBU_LOG_LEVEL' % service_name, 'WARN'))


def configure_logging(level_env_var, time_env_var):
    if int(os.environ.get(time_env_var, "1")):
        format_str = '%(asctime)s '
    else:
        format_str = ''
    format_str += '%(levelname)5s ' + colored('[%(name)s] ', 'green')
    format_str += '%(message)s'

    logging.basicConfig(
        format=format_str,
        level=os.environ.get(level_env_var, 'INFO').upper())


def log_response(logger):
    def _log_response(target):
        def wrapper(*args, **kwargs):
            body, code = target(*args, **kwargs)

            logger.info("Responded %s to %s  %s",
                        code, target.__name__.upper(), request.url)
            logger.debug("    Body: %s", body)
            return body, code
        return wrapper
    return _log_response


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
