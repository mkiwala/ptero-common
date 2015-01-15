import abc
from urlparse import urlparse, urlunparse


class Janitor(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, url):
        self.url_obj = urlparse(url)
        self.sanitized_url = self.sanitize_url(self.url_obj)

    @abc.abstractmethod
    def clean(self):  # pragma: no cover
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
