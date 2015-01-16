import argparse
import logging
import os
import sys


__all__ = ['perform_cleanup']


LOG = logging.getLogger(__name__)


def perform_cleanup(janitor_factory=None, required_envvars=None):
    init()
    validate_perform_cleanup_args(janitor_factory, required_envvars)

    try:
        janitors = janitor_factory()
    except:
        LOG.exception('Failed to construct all janitors')
        sys.exit(1)

    for janitor in janitors:
        try:
            janitor.clean()
        except:
            LOG.exception('Janitor %s failed to cleanup', janitor)
            sys.exit(1)


def validate_allowed(force):
    if (not force) and not os.environ.get('PTERO_ALLOW_JANITORS'):
        LOG.error('PTERO_ALLOW_JANITORS not set, and --force not given')
        sys.exit(1)


def validate_environment(required_envvar_names):
    errors = []
    for varname in required_envvar_names:
        if varname not in os.environ:
            errors.append('%s is not set' % varname)

    if errors:
        for error in sorted(errors):
            LOG.error('%s', error)
        sys.exit(1)


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('--force', action='store_true', default=False,
                        help='Purge regardless of PTERO_ALLOW_JANITORS')

    parser.add_argument('--log-level', dest='log_level', default='WARN')

    return parser.parse_args()


def init():
    args = parse_args()
    logging.basicConfig(level=args.log_level)
    validate_allowed(args.force)


def validate_perform_cleanup_args(janitor_factory, required_envvars):
    if required_envvars:
        validate_environment(required_envvars)

    if not callable(janitor_factory):
        LOG.error('janitor_factory must be callable')
        sys.exit(1)
