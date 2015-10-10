from termcolor import colored
import requests
from requests.models import Request
from requests.exceptions import ConnectionError
import logging
import os
from pprint import pformat
from pythonjsonlogger import jsonlogger
import sys
import traceback

MAX_DATA_LENGTH = int(os.environ.get("PTERO_LOG_MAX_DATA_LENGTH", "512"))
TRACEBACK_DEPTH = int(os.environ.get("PTERO_LOG_EXCEPTION_TRACEBACK_DEPTH", "3"))

try:
    from flask import request
    from werkzeug.wrappers import BaseResponse as Response
except:
    # Not everybody who uses ptero_common has requires/uses flask
    pass


class CustomFormatter(logging.Formatter):
    def formatException(self, exc_info):
        return ''.join(traceback.format_tb(
            sys.exc_info()[2], TRACEBACK_DEPTH)) + _pformat(sys.exc_info()[1])


def log_exception(logger, *args, **kwargs):
    if 'extra' in kwargs:
        my_extra = kwargs['extra'].copy()
    else:
        my_extra = {}

    my_extra['exception'] = _pformat(sys.exc_info()[1])
    for i, tb_line in enumerate(
            traceback.format_tb(sys.exc_info()[2], TRACEBACK_DEPTH)):
        my_extra['traceback-%s' % (i+1)] = tb_line

    logger.warn(_pformat(my_extra))
    kwargs['extra'] = my_extra
    logger.exception(*args, **kwargs)


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
    format_str += '%(levelname)5s '
    format_str += '%(message)s'

    if int(os.environ.get('PTERO_LOG_FORMAT_JSON', "0")):
        formatter = jsonlogger.JsonFormatter(format_str)
    else:
        formatter = CustomFormatter(format_str)

    logHandler = logging.StreamHandler()
    logHandler.setFormatter(formatter)

    logger = logging.getLogger()
    logger.addHandler(logHandler)

    logger.setLevel(os.environ.get(level_env_var, 'INFO').upper())


def logged_response(logger):
    def _log_response(target):
        def wrapper(*args, **kwargs):
            label = '%s %s' % (target.__name__.upper(), request.url)
            logger.info(
                "Handling %s from %s", label, request.access_route[0])

            request_data = _pformat(getattr(request, '_cached_data', None))
            logger.debug("Body of %s: %s", label, request_data)

            try:
                result = target(*args, **kwargs)
            except Exception:
                logger.exception(
                    "Exception while handling %s from %s:\n"
                    "Body: %s", label, request.access_route[0], request_data)
                raise
            response = Response(*result)
            logger.info(
                "Responding %s to %s", response.status_code, label)

            logger.debug("Full response to %s: %s", label, _pformat(result))
            return result
        return wrapper
    return _log_response


def _pformat(data):
    return pformat(data, indent=2, width=80)[:MAX_DATA_LENGTH]


def _log_request(target, kind):
    def wrapper(*args, **kwargs):

        logger = kwargs.get('logger', logging.getLogger(__name__))
        if 'logger' in kwargs:
            del kwargs['logger']

        kwargs_for_constructor = kwargs.copy()
        if 'timeout' in kwargs_for_constructor:
            # timout is an argument to requests.get/post/ect but not
            # Request.__init__
            del kwargs_for_constructor['timeout']
        request = Request(kind.upper(), *args, **kwargs_for_constructor)

        label = '%s %s' % (kind.upper(), request.url)
        logger.info('Sending %s', label)
        logger.debug("Params for %s: %s", label, _pformat(request.params))
        logger.debug("Headers for %s: %s", label, _pformat(request.headers))
        logger.debug("Data for %s: %s", label, _pformat(request.data))

        try:
            response = target(*args, **kwargs)
        except ConnectionError:
            raise
        except Exception as e:
            logger.exception(
                "Exception while sending %s:\n"
                "  Args: %s\n"
                "  Keyword Args: %s",
                label, _pformat(args), _pformat(kwargs))
            raise


        logger.info("Got %s from %s", response.status_code, label)
        logger.debug("Body of response from %s: %s", label,
                _pformat(response.text))
        logger.debug("Headers in response from %s: %s", label,
                _pformat(response.headers))

        return response
    return wrapper


class LoggedRequest(object):
    def __getattr__(self, name):
        return _log_request(getattr(requests, name), name)
logged_request = LoggedRequest()
