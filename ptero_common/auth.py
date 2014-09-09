from flask import request, Response
import re

class ProtectedEndpoint(object):
    def __init__(self, scopes=[], claims=[], audiences=[]):
        self.scopes = scopes
        self.claims = claims
        self.audiences = audiences

    def __call__(self, target):
        def handle_request(*args, **kwargs):
            response, id_token = _parse_request(request, self.scopes,
                    self.claims, self.audiences)
            if (response):
                return response
            else:
                return target(*args, id_token=id_token, **kwargs)
        return handle_request

protected_endpoint = ProtectedEndpoint


def _parse_request(request, scopes, claims, audiences):
    if ('Authorization' not in request.headers or
            'Identity' not in request.headers):
        return Response(status=401,
                headers={'WWW-Authenticate': authenticate_value_text(scopes),
                         'Identify': identify_value_text(claims, audiences)}), None

    try:
        access_token = parse_authorization_text(request.headers['Authorization'])
    except ValueError as e:
        return Response(status=400,
                headers={'WWW-Authenticate':
                        '%s, error="invalid_request", error_description="The Bearer token is malformed"' %
                        (authenticate_value_text(scopes)),
                        'Identify': identify_value_text(claims, audiences)}), None

    return None, None


def authenticate_value_text(scopes):
    return 'Bearer realm="PTero", scope="%s"' % ' '.join(scopes)

def identify_value_text(claims, audiences):
    return 'ID Token claims="%s", aud="%s"' % (', '.join(claims),
            ', '.join(audiences))

def parse_authorization_text(text):
    match_object = re.search('Bearer (.*)', text)
    if match_object is None:
        raise ValueError('Cannot parse authorization_text (%s)' % text)
    else:
        return match_object.groups()[0]
