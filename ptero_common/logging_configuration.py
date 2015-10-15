import logging
from ptero_common.nicer_logging import CustomFormatter
import os
from pythonjsonlogger import jsonlogger


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
