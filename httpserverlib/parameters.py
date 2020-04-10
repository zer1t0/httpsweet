import json
from urllib.parse import parse_qs
from .constants import Action, ContentType, QueryStringKeys
from .encoder import EncoderFactory
from .utils import lower_dict_keys


class ParametersBuilder(object):
    """Helper to collect the parameters from different parts of the request and
    build a Parameters class.

    It collects the parameters from:
    * Request Method
    * Url path
    * Url query string
    * Body, which can be:
        + raw data
        + a query string
        + json data
    """

    def __init__(
            self,
            action=None,
            path=None,
            offset=None,
            size=None,
            encoding=None,
            append=None,
            data=None
    ):
        self.action = action
        self.path = path
        self.offset = offset
        self.size = size
        self.encoding = encoding
        self.append = append
        self.data = data

    def build(self):
        if self.offset is None:
            offset = 0
        else:
            offset = int(self.offset)

        if self.size is not None:
            size = int(self.size)
        else:
            size = self.size

        if self.data is None:
            data = b""
        else:
            data = self.data

        return Parameters(
            action=self.action,
            path=self.path,
            offset=offset,
            size=size,
            encoder=EncoderFactory.create(self.encoding),
            append=bool(self.append),
            data=data
        )

    @classmethod
    def from_request(cls, request):
        builder = cls()
        builder.update_from_method(request.method)
        builder.update_from_path(request.path)
        builder.update_from_query_string(request.url.query_string)
        builder.update_from_request_content(request)
        builder.update_from_dictionary(request.headers)
        return builder

    def update_from_request_content(self, request):
        content_length = request.content_length
        if content_length > 0:
            content = request.rfile.read(content_length)
            if request.content_type == ContentType.URLENCODED:
                self.update_from_query_string_bytes(parse_qs(content))
            elif request.content_type == ContentType.JSON:
                self.update_from_dictionary(json.loads(content))
            else:
                self.update_from_raw_data(content)

    def update_from_method(self, method):
        other = self.from_method(method)
        self.update(other)

    @classmethod
    def from_method(cls, method):
        if method == "POST" or method == "PUT":
            return cls(action=Action.UPLOAD)
        else:
            return cls(action=Action.DOWNLOAD)

    def update_from_path(self, path):
        other = self.from_path(path)
        self.update(other)

    @classmethod
    def from_path(cls, path):
        return cls(path=path)

    def update_from_query_string(self, qs):
        other = self.from_query_string(qs)
        self.update(other)

    @classmethod
    def from_query_string(cls, qs):
        d = {}
        for member in QueryStringKeys:
            key = member.value
            if key in qs:
                if key == QueryStringKeys.data.value:
                    d[key] = qs[key][0].encode()
                else:
                    d[key] = qs[key][0]

        return cls.from_dictionary(d)

    def update_from_query_string_bytes(self, qs):
        other = self.from_query_string_bytes(qs)
        self.update(other)

    @classmethod
    def from_query_string_bytes(cls, qs):
        d = {}
        for member in QueryStringKeys:
            key = member.value
            key_bytes = key.encode()
            if key_bytes in qs:
                if key == QueryStringKeys.data.value:
                    d[key] = qs[key_bytes][0]
                else:
                    d[key] = qs[key_bytes][0].decode()

        return cls.from_dictionary(d)

    def update_from_dictionary(self, d):
        other = self.from_dictionary(d)
        self.update(other)

    @classmethod
    def from_dictionary(cls, d):
        lower_d = lower_dict_keys(d)
        append = "append" in lower_d
        return cls(
            action=lower_d.get("action", None),
            path=lower_d.get("path", None),
            offset=lower_d.get("offset", None),
            size=lower_d.get("size", None),
            encoding=lower_d.get("encoding", None),
            append=append,
            data=lower_d.get("data", None)
        )

    def update_from_raw_data(self, raw_data):
        other = self.from_raw_data(raw_data)
        self.update(other)

    @classmethod
    def from_raw_data(cls, raw_data):
        return cls(data=raw_data)

    def update(self, other):
        for key, value in other.__dict__.items():
            if value is not None:
                self.__dict__[key] = value


class Parameters:
    """Store the parameters received from a request."""

    def __init__(
            self,
            action,
            path,
            offset,
            size,
            encoder,
            append,
            data
    ):
        self.action = action
        self.path = path
        self.offset = offset
        self.size = size
        self.encoder = encoder
        self.append = append
        self.data = data

    @classmethod
    def from_request(cls, request):
        return ParametersBuilder.from_request(request).build()

    def __repr__(self):
        return repr(self.__dict__)
