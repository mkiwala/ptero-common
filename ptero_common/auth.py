from flask import request, Response
import jot
import re

class MissingAuthHeadersError(Exception): pass
class MalformedAccessTokenError(Exception): pass

class ProtectedEndpoint(object):
    def __init__(self, scopes=[], claims=[], audiences=[]):
        self.scopes = scopes
        self.claims = claims
        self.audiences = audiences

    def __call__(self, target):
        self.target = target
        return self._execute_target

    def _execute_target(self, *args, **kwargs):
        response, id_token = _parse_request(request, self.scopes,
                self.claims, self.audiences)
        if (response):
            return response
        else:
            return self.target(*args, id_token=id_token, **kwargs)

protected_endpoint = ProtectedEndpoint


def _parse_request(request, scopes, claims, audiences):
    try:
        ensure_headers_are_present(request)
    except MissingAuthHeadersError:
        return Response(status=401,
                headers={'WWW-Authenticate': authenticate_value_text(scopes),
                         'Identify': identify_value_text(claims, audiences)}), None

    try:
        access_token = parse_authorization_text(request.headers['Authorization'])
    except MalformedAccessTokenError as e:
        return Response(status=400,
                headers={'WWW-Authenticate':
                        '%s, error="invalid_request", error_description="The Bearer token is malformed"' %
                        (authenticate_value_text(scopes)),
                        'Identify': identify_value_text(claims, audiences)}), None
    try:
        id_token = jot.deserialize(request.headers['Identity'])
    except:
        return Response(status=400,
                headers={'WWW-Authenticate': authenticate_value_text(scopes),
                        'Identify': '%s, error="invalid_request", error_description="The ID token is malformed"'
                        % identify_value_text(claims, audiences)}), None


    return None, None

def ensure_headers_are_present(request):
    if ('Authorization' not in request.headers or
            'Identity' not in request.headers):
        raise MissingAuthHeadersError

def authenticate_value_text(scopes):
    return 'Bearer realm="PTero", scope="%s"' % ' '.join(scopes)

def identify_value_text(claims, audiences):
    return 'ID Token claims="%s", aud="%s"' % (', '.join(claims),
            ', '.join(audiences))

def parse_authorization_text(text):
    match_object = re.search('Bearer (.*)', text)
    if match_object is None:
        raise MalformedAccessTokenError
    else:
        return match_object.groups()[0]
