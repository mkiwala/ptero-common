import celery
import logging
import requests
import json
from requests.exceptions import ConnectionError
from ptero_common.logging_configuration import logged_request

__all__ = ['HTTP', 'HTTPWithResult']


LOG = logging.getLogger(__name__)

MIN = 60
DELAYS = [1, 5, 10, 30, 60, 2*MIN, 4*MIN, 10*MIN, 30*MIN, 60*MIN]
DELAYS.extend([60*MIN for i in range(72)])


class HTTP(celery.Task):
    ignore_result = True
    max_retries = len(DELAYS)

    def run(self, method, url, **kwargs):
        try:
            response = getattr(logged_request, method.lower())(
                url, data=self.body(kwargs),
                headers={'Content-Type': 'application/json'},
                timeout=10, logger=LOG)
        except ConnectionError as exc:
            delay = DELAYS[self.request.retries]
            LOG.info(
                "A ConnectionError occured for while attempting to send "
                "%s  %s, retrying in %s seconds. Attempt %d of %d.",
                method.upper(), url, delay, self.request.retries+1,
                self.max_retries+1)
            self.retry(exc=exc, countdown=delay)

        if response.status_code >= 500:
            delay = DELAYS[self.request.retries]
            LOG.info(
                "Got response (%s), retrying in %s seconds.  Attempt %d of %d.",
                response.status_code, delay, self.request.retries+1,
                self.max_retries+1)
            self.retry(
                exc=celery.exceptions.MaxRetriesExceeded,
                countdown=delay)

        return response.json()

    def body(self, kwargs):
        return json.dumps(kwargs)

class HTTPWithResult(HTTP):
    ignore_result = False
