from urllib.parse import urlparse, parse_qs
from .constants import Headers
from .utils import lower_dict_keys
from http import cookies


class RequestInfo(object):
    """Store useful information about the request such as:
        + Method
        + Url
        + Headers
        + Cookies
        + Buffer to read the body
    """

    def __init__(self, method, url, headers, rfile):
        self.method = method
        self.url = Url(url)
        self.headers = lower_dict_keys(headers)
        self.rfile = rfile
        self.cookies = self._get_cookies_from_headers()

    def _get_cookies_from_headers(self):
        c = cookies.SimpleCookie(self.headers.get("cookie", ""))
        cookies_dict = {}
        for key, value in c.items():
            cookies_dict[key.lower()] = value.value

        return cookies_dict

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


class Url:
    """Store useful information of the request url, such as:
        + Path
        + Query string
    """

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
