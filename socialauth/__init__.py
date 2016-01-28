class Error(Exception):
    def __init__(self, message):
        Exception.__init__(self)
        self.message = message

    def __str__(self):
        return repr(self.message)


class InvalidUsage(Exception):
    def __init__(self, message, status_code = 400):
        Exception.__init__(self)
        self.message     = message
        self.status_code = status_code

    def __str__(self): # pragma: no cover
        return '({}) {}'.format(repr(self.status_code), repr(self.message))

    def to_dict(self): # pragma: no cover
        return {
            'errors': [{
                'status': self.status_code,
                'title': self.message
            }]
        }

from .authentication import http_get_provider
