import argparse
import logging
import os
import sys


__all__ = ['perform_cleanup']


LOG = logging.getLogger(__name__)


def perform_cleanup(janitor_spec):
    args = parse_args(janitor_spec)
    logging.basicConfig(level=args.log_level)
    validate_allowed(args.force)
    validate_janitor_spec(janitor_spec)

    for janitor_name, janitor in janitor_spec.iteritems():
        if janitor['do_cleanup']:
            _perform_cleanup(janitor_name, janitor)


def _perform_cleanup(janitor_name, janitor):
    try:
        janitor['cleanup_action']()
    except:
        LOG.exception('Janitor %s failed to cleanup', janitor_name)
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


def validate_janitor_spec(janitor_spec):
    for janitor_name, janitor in janitor_spec.iteritems():
        if janitor['do_cleanup']:
            _validate_janitor_spec(janitor_name, janitor)


def _validate_janitor_spec(janitor_name, janitor):
    if janitor['required_envvars']:
        validate_environment(janitor['required_envvars'])

    if not callable(janitor['cleanup_action']):
        LOG.error('cleanup_action for %s must be callable' % janitor_name)
        sys.exit(1)


def parse_args(janitor_spec):
    parser = argparse.ArgumentParser()

    parser.add_argument('--force', action='store_true', default=False,
                        help='Purge regardless of PTERO_ALLOW_JANITORS')

    parser.add_argument('--log-level', dest='log_level', default='WARN')

    parser.add_argument('--all', action='store_true', default=False)

    for k in janitor_spec.keys():
        parser.add_argument('--%s' % k, action='store_true', default=False)

    args = parser.parse_args()

    for k in janitor_spec.keys():
        janitor_spec[k].update({'do_cleanup':
            getattr(args, k) or args.all})

    return args
