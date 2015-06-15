from termcolor import colored
import requests
from requests.models import Request
from requests.exceptions import ConnectionError
import logging
import os
from pprint import pformat
from pythonjsonlogger import jsonlogger

try:
    from flask import request
    from werkzeug.wrappers import BaseResponse as Response
except:
    # Not everybody who uses ptero_common has requires/uses flask
    pass

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        jsonlogger.JsonFormatter.add_fields(self, log_record, record,
                message_dict)
        if hasattr(request, "workflow_id"):
            log_record['workflowId'] = request.workflow_id

        log_record['component'] = 'PTero'

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


def configure_web_logging(service_name):
    configure_logging(
        'PTERO_%s_LOG_LEVEL' % service_name,
        'PTERO_%s_LOG_WITH_TIMESTAMPS' % service_name)
    logging.getLogger('pika').setLevel(
        os.environ.get('PTERO_%s_PIKA_LOG_LEVEL' % service_name, 'WARN'))
    logging.getLogger('requests').setLevel(
        os.environ.get('PTERO_%s_REQUESTS_LOG_LEVEL' % service_name, 'WARN'))
    logging.getLogger('werkzeug').setLevel(
        os.environ.get('PTERO_%s_WERKZEUG_LOG_LEVEL' % service_name, 'WARN'))


def configure_logging(level_env_var, time_env_var):
    if int(os.environ.get(time_env_var, "1")):
        format_str = '%(asctime)s '
    else:
        format_str = ''
    format_str += '%(levelname)5s ' + colored('[%(name)s] ', 'green')
    format_str += '%(message)s'

    if int(os.environ.get('PTERO_LOG_FORMAT_JSON', "0")):
        formatter = CustomJsonFormatter(format_str + '%s(workflowId)' +
                '%s(component)')
    else:
        formatter = logging.Formatter(format_str)

    logHandler = logging.StreamHandler()
    logHandler.setFormatter(formatter)

    logger = logging.getLogger()
    logger.addHandler(logHandler)

    logger.setLevel(os.environ.get(level_env_var, 'INFO').upper())


def logged_response(logger):
    def _log_response(target):
        def wrapper(*args, **kwargs):
            try:
                result = target(*args, **kwargs)
            except Exception as e:
                logger.exception(
                    "Unexpected exception while handling %s  %s:\n"
                    "Body: %s\n%s",
                    target.__name__.upper(), request.url, request.data, str(e))
                raise
            response = Response(*result)
            logger.info(
                "Responded %s to %s  %s",
                response.status_code, target.__name__.upper(), request.url)
            logger.debug("    Returning: %s",
                         pformat(result, indent=2, width=80))
            return result
        return wrapper
    return _log_response


def _log_request(target, kind):
    def wrapper(*args, **kwargs):
        logger = kwargs.get('logger', logging.getLogger(__name__))
        if 'logger' in kwargs:
            del kwargs['logger']

        try:
            response = target(*args, **kwargs)
        except ConnectionError:
            raise
        except Exception as e:
            logger.exception(
                "Unexpected exception while sending %s request\n"
                "Args: %s\n"
                "Keyword Args: %s\n"
                "Exception: %s\n",
                kind.upper(), pformat(args), pformat(kwargs), str(e))
            raise

        if 'timeout' in kwargs:
            # timout is an argument to requests.get/post/ect but not
            # Request.__init__
            del kwargs['timeout']
        r = Request(kind.upper(), *args, **kwargs)

        logger.info("%s from %s  %s", response.status_code, kind.upper(), r.url)
        for name in ['params', 'headers', 'data']:
            logger.debug("    %s%s: %s", name[0].upper(), name[1:],
                         pformat(getattr(r, name), indent=2, width=80))

        return response
    return wrapper


class LoggedRequest(object):
    def __getattr__(self, name):
        return _log_request(getattr(requests, name), name)
logged_request = LoggedRequest()
