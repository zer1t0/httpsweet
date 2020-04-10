from enum import Enum
from .constants import Actions
from .encoder import EncoderFactory


class QueryStringKeys(Enum):
    action = "action"
    path = "path"
    offset = "offset"
    size = "size"
    encoding = "encoding"
    append = "append"
    data = "data"


class ParametersBuilder(object):

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

    def update_from_method(self, method):
        other = self.from_method(method)
        self.update(other)

    @classmethod
    def from_method(cls, method):
        if method == "POST" or method == "PUT":
            return cls(action=Actions.UPLOAD_FILE)
        else:
            return cls(action=Actions.DOWNLOAD_FILE)

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
        append = "append" in d
        return cls(
            action=d.get("action", None),
            path=d.get("path", None),
            offset=d.get("offset", None),
            size=d.get("size", None),
            encoding=d.get("encoding", None),
            append=append,
            data=d.get("data", None)
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

    def __repr__(self):
        return repr(self.__dict__)
