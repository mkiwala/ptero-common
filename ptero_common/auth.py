from flask import request, Response


def protected_endpoint(target):
    def handle_request(*args, **kwargs):
        response, id_token = _parse_request(request)
        if (response):
            return response
        else:
            return target(*args, id_token=id_token, **kwargs)
    return handle_request

def _parse_request(request):
    if ('Authorization' not in request.headers or
            'Identity' not in request.headers):
        return Response(status=401,
                headers={'WWW-Authenticate': 'Bearer realm="PTero"'}), None
    else:
        return None, None
