from rest_framework.exceptions import APIException

class ServiceUnavailable(APIException):
    status_code = 503
    default_detail = 'Unable to perform the action.'
    default_code = 'Service unavailable.'



class ServerConnectionError(APIException):
    status_code = 502
    default_detail = 'Unable to connect to Upstream Server'
    default_code = 'Service unavailable.'


