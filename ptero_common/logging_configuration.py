from termcolor import colored
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
