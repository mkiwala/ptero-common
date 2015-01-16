from .base import Janitor
import logging
import redis


LOG = logging.getLogger(__name__)


class RedisJanitor(Janitor):
    ALLOWED_SCHEMES = {'redis'}

    def clean(self):
        LOG.debug('Flushing all keys at %s', self.sanitized_url)
        connection = redis.Redis(host=self.host, port=self.port)
        connection.flushall()

    @property
    def host(self):
        return self.url_obj.hostname

    @property
    def port(self):
        return self.url_obj.port
