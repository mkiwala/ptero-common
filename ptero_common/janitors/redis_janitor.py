from .base import Janitor
from ptero_common import nicer_logging
import redis


LOG = nicer_logging.getLogger(__name__)


class RedisJanitor(Janitor):
    ALLOWED_SCHEMES = {'redis'}

    def clean(self):
        LOG.debug('Flushing all keys at %s', self.sanitized_url)
        if self.port is None:
            connection = redis.Redis(host=self.host)
        else:
            connection = redis.Redis(host=self.host, port=self.port)
        connection.flushall()

    @property
    def host(self):
        return self.url_obj.hostname

    @property
    def port(self):
        return self.url_obj.port
