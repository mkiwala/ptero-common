from unittest import TestCase
import flask
from flask import request
from ptero_common.auth import protected_endpoint

app = flask.Flask('test_app')

@protected_endpoint(scopes=['a','b'], claims=['c','d'], audiences=['e','f'])
def target(*args, **kwargs):
    return 'test_return_value'

VALID_ID_TOKEN = ('eyJhbGciOiJSU0ExXzUiLCJjdHkiOiJKV1QiLCJlbmMiOiJBMTI4Q0JDLU'
        'hTMjU2Iiwia2lkIjoiU09NRSBGQU5DWSBLSUQifQ.CSQDZ8fcAgUnioPazyirXFwzZd'
        'sEiVLFpHVNJHkilzEaiI_PnPM8vkh9TqULxJcyzZDrAUBDhtc4Q_FHNK0FN4ngJccY4'
        'Ns2qOA_DSsBnYVuB1aG-EUQ85cqoWQvxS1UjZ7zXV0N3D_KS2UX92argCjg055GUiMm'
        'IIzvntND4k9bMc4pL9jEUGKsTNrkHtZLjd3r--DMfHhnRhmGNwRbaFrEGuJshNJZAyp'
        '3DlwVcD_-CHmdrST3_1M49DnSnI3ytthSuAHGKeths5piHpDBVJsQ58WiZgcKJeNPlZ'
        'XHQRqgwZj4gVyzVd4lHG2yHraa21P41gVM81lSCJisKGPtTw.GXcxNkIbM21Rd2OQj2'
        'ib5w.En89jY7MnIcUgMZt2l9rlbgARVSxgaRPwNO3UPoYQO5-W0rmfk4GLIpbaXkfMF'
        'wK1JdGlefyKW0me7T3Wsd2FSWI0zYV8B5_EduL6GLsUBQpJH2eD-mSSyGjR9D3GV9Fo'
        'AWOAMXoBtk4iLPTQnOLMGL5J3oRKRcUKvFO2zBGciC4b-EDn-zUJJEqHwl4BJ7Rr-mI'
        'clhDAMYNSO4LN0cgS8dSTyfQhMorsuahptOSoTP2mJaA2v2bG0VKeIyEOx8RgwK1z6D'
        'yoTsMlgFrpteFbzRz2H2w7gKrItnqSAFQa8JUd-BvpVEXdPYfH41MHPGeUOHd9L7RO6'
        'HSTrsoQb_wf6A3NYtIuMfTIR6nwsKBMB8i6QtkhoTTAFq2xneAg4JbmljiM9As9CbxW'
        'a7SAH3Xs9sVi2F0-1lZYFaKRTxswadhn64X0KNf6jUIMFYamkGkNcHApsERz1PROmCF'
        'k9WusVrZBW5eirunPIAEdEYC8QxpqmicHeRrtFa0Vjr7FojJ6o8bUsblKaGXDXhpQGa'
        'F40H0TNqBEllIXTln9J6jz8u0DjocPCMy8v0_QGlshGJypjo_NehwvKRrwaSTv3NoEl'
        'VGb10L7ZFF9RincIMJG7nFSfuTzMNfYVn0CvOwwlkIkoYm2oaIoilxlOTSXf63ypd45'
        'Mp5DF99vFqL_-Zp1T-QIDsVSvm3MIOo1hc5XgxvdGsbAl3ZkCF9GUU6yXDnXX56Qp9a'
        'Nw-TuhQyaW1J-Nw4MeHeg7JVFf5oqwrLS60iJ7kWYSY5qV58keAfbX4gYS44y7GI_H6'
        'ctq62BiFSivDRxaqp2tKNhFQzBSiXNLVwCaRsVhTV_tC0FpOkcQlh0wHOhv_brPK42M'
        'q_GlAOYo--q5glR7_7cmhErVfQt6HMiZZ3omwJ9jLGrFsfvh_TCA.hzX35A0ZuHOqyT'
        '4xI9GZiA')
VALID_HEADER = {'Authorization':'Bearer 1234', 'Identity':VALID_ID_TOKEN}
BAD_AUTHORIZATION_HEADER = {'Authorization':'foo', 'Identity':VALID_ID_TOKEN}
BAD_IDENTITY_HEADER = {'Authorization':'Bearer 1234', 'Identity':'foo'}

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

    def test_invalid_identity_header_returns_400(self):
        with app.test_request_context(headers=BAD_IDENTITY_HEADER):
            return_value = target()
            self.assertEqual(return_value.status, '400 BAD REQUEST')

    def test_invalid_identity_header_returns_identify_headers(self):
        with app.test_request_context(headers=BAD_IDENTITY_HEADER):
            return_value = target()
            self.assertTrue('WWW-Authenticate' in return_value.headers)

            self.assertEqual(return_value.headers['Identify'],
                    'ID Token claims="c, d", aud="e, f", error="invalid_request", error_description="The ID token is malformed"')
