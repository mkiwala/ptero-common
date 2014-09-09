from unittest import TestCase
import flask
from flask import request
from ptero_common.auth import protected_endpoint

app = flask.Flask('test_app')

@protected_endpoint(scopes=['a','b'], claims=['c','d'], audiences=['e','f'])
def target(*args, **kwargs):
    return 'test_return_value'

VALID_HEADER = {'Authorization':'Bearer 1234', 'Identity':'bar'}
BAD_AUTHORIZATION_HEADER = {'Authorization':'foo', 'Identity':'bar'}

class TestRequestParser(TestCase):
    def test_no_authorization_returns_401(self):
        with app.test_request_context(headers=None):
            return_value = target()
            self.assertEqual(return_value.status, '401 UNAUTHORIZED')

    def test_no_authorization_returns_authenticate_headers(self):
        with app.test_request_context(headers=None):
            return_value = target()
            self.assertTrue('WWW-Authenticate' in return_value.headers)

            self.assertEqual(return_value.headers['WWW-Authenticate'],
                    'Bearer realm="PTero", scope="a b"')

    def test_no_authorization_returns_identify_headers(self):
        with app.test_request_context(headers=None):
            return_value = target()
            self.assertTrue('Identify' in return_value.headers)

            self.assertEqual(return_value.headers['Identify'],
                    'ID Token claims="c, d", aud="e, f"')


    def test_returns_targets_result(self):
        with app.test_request_context(headers=VALID_HEADER):
            return_value = target()
            self.assertEqual(return_value, 'test_return_value')

    def test_adds_id_token_as_kwarg(self):
        @protected_endpoint()
        def echo_target(*args, **kwargs):
            return (args, kwargs)

        with app.test_request_context(headers=VALID_HEADER):
            return_value = echo_target(1,2,3, kw='foo')
            self.assertEqual(return_value, ((1,2,3), {'kw':'foo','id_token':None}))


    def test_invalid_authorization_header_returns_400(self):
        with app.test_request_context(headers=BAD_AUTHORIZATION_HEADER):
            return_value = target()
            self.assertEqual(return_value.status, '400 BAD REQUEST')

    def test_invalid_authorization_header_returns_authenticate_headers(self):
        with app.test_request_context(headers=BAD_AUTHORIZATION_HEADER):
            return_value = target()
            self.assertTrue('WWW-Authenticate' in return_value.headers)

            self.assertEqual(return_value.headers['WWW-Authenticate'],
                    'Bearer realm="PTero", scope="a b", error="invalid_request", error_description="The Bearer token is malformed"')
