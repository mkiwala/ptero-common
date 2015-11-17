import re
import os
from ptero_common import nicer_logging

LOG = nicer_logging.getLogger(__name__)

_CONFIGURATION_NAMES = {
        'CELERY_BROKER_URL': 'BROKER_URL',
        'CELERY_BROKER_HEARTBEAT': 'BROKER_HEARTBEAT',
        'CELERY_BROKER_HEARTBEAT_CHECKRATE': 'BROKER_HEARTBEAT_CHECKRATE',
        'CELERY_BROKER_TRANSPORT_OPTIONS': 'BROKER_TRANSPORT_OPTIONS',
}


def _default_celery_config_name(env_var_name):
    m = re.search('CELERY', env_var_name)
    return env_var_name[m.start():]


def _get_celery_config_name(env_var_name):
    default = _default_celery_config_name(env_var_name)
    return _CONFIGURATION_NAMES.get(default, default)


def _default_formatter(value):
    return value


def _list_formatter(value):
    return value.split(':')


def _bool_formatter(value):
    return bool(int(value))


def _json_formatter(value):
    return json.loads(value)

_FORMATTERS = {
        'CELERY_ACCEPT_CONTENT': _list_formatter,
        'CELERY_ACKS_LATE': _bool_formatter,
        'CELERY_BROKER_HEARTBEAT': float,
        'CELERY_BROKER_HEARTBEAT_CHECKRATE': float,
        'CELERY_BROKER_TRANSPORT_OPTIONS': _json_formatter,
        'CELERY_PREFETCH_MULTIPLIER': int,
        'CELERY_TRACK_STARTED': _bool_formatter,
}


def _get_formatter(config_name):
    return _FORMATTERS.get(config_name, _default_formatter)


def get_config_from_env(service_name):
    result = {}
    for env_var_name, env_var_value in os.environ.iteritems():
        if re.match('PTERO_%s_CELERY' % service_name, env_var_name):
            config_name = _get_celery_config_name(env_var_name)
            formatter = _get_formatter(config_name)
            config_value = formatter(env_var_value)

            result[config_name] = config_value
            LOG.debug("Celery config %s=%s derived based on shell environment "
                "%s=%s",
                    config_name, str(config_value), env_var_name, env_var_value)

    return result
