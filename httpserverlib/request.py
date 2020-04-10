from urllib.parse import urlparse, parse_qs
from .constants import Headers


class RequestInfo(object):

    def __init__(self, method, url, headers, rfile):
        self.method = method
        self.url = Url(url)
        self.headers = self._generate_lower_keys(headers)
        self.rfile = rfile

    @classmethod
    def from_request_handler(cls, request_handler):
        return cls(
            method=request_handler.command,
            url=request_handler.path,
            headers=request_handler.headers,
            rfile=request_handler.rfile
        )

    @property
    def content_type(self):
        return self.headers.get(Headers.CONTENT_TYPE.lower(), "")

    @property
    def content_length(self):
        return int(self.headers.get(Headers.CONTENT_LENGTH.lower(), "0"))

    @property
    def path(self):
        return self.url.path

    @staticmethod
    def _generate_lower_keys(d):
        other_d = {}
        for key, value in d.items():
            other_d[key.lower()] = value
        return other_d


class Url:

    def __init__(self, url_str):
        self._url = urlparse(url_str)
        self._parameters = parse_qs(self._url.query)

    @property
    def action(self):
        try:
            return self.args["action"][0]
        except KeyError:
            return None

    @property
    def path(self):
        return self._url.path

    @property
    def args(self):
        return self._parameters

    @property
    def query_string(self):
        return self._parameters
