from .exceptions import JanitorException
from urlparse import urlparse, urlunparse
import abc


class Janitor(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, url):
        self.url = url
        self.url_obj = urlparse(url)
        self.sanitized_url = self.sanitize_url(self.url_obj)

        if self.url_obj.scheme not in self.ALLOWED_SCHEMES:
            raise JanitorException('Scheme "%s" not allowed.  '
                    'Expected something from: %s' %
                    (self.url_obj.scheme, self.ALLOWED_SCHEMES))

    @abc.abstractmethod
    def clean(self):  # pragma: no cover
        return NotImplemented

    @abc.abstractproperty
    def ALLOWED_SCHEMES(self):  # pragma: no cover
        return NotImplemented

    @staticmethod
    def sanitize_url(url_obj):
        return urlunparse((url_obj.scheme, _sanitize_netloc(url_obj),
                           url_obj.path, '', '', ''))


def _sanitize_netloc(url_obj):
    result = ''

    if url_obj.username:
        result += '%s:*@' % url_obj.username

    result += url_obj.hostname

    if url_obj.port:
        result += ':%s' % url_obj.port

    return result
