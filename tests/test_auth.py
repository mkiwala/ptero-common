from unittest import TestCase
import flask
from flask import request
from ptero_common.auth import protected_endpoint

app = flask.Flask('test_app')

@protected_endpoint
def target(*args, **kwargs):
    return 'test_return_value'

VALID_HEADER = {'Authorization':'foo', 'Identity':'bar'}

class TestRequestParser(TestCase):
    def test_request_with_no_authorization_returns_401(self):
        with app.test_request_context(headers=None):
            return_value = target()
            self.assertEqual(return_value.status, '401 UNAUTHORIZED')

    def test_request_with_authorization_returns_targets_result(self):
        with app.test_request_context(headers=VALID_HEADER):
            return_value = target()
            self.assertEqual(return_value, 'test_return_value')

    def test_adds_id_token_as_kwarg(self):
        @protected_endpoint
        def echo_target(*args, **kwargs):
            return (args, kwargs)

        with app.test_request_context(headers=VALID_HEADER):
            return_value = echo_target(1,2,3, kw='foo')
            self.assertEqual(return_value, ((1,2,3), {'kw':'foo','id_token':None}))
