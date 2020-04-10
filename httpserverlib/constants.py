from enum import Enum


class ContentType:
    JSON = "application/json"
    URLENCODED = "application/x-www-form-urlencoded"
    OCTET_STREAM = "application/octet-stream"


class Headers:
    CONTENT_TYPE = "Content-Type"
    CONTENT_LENGTH = "Content-Length"


class Action:
    DOWNLOAD = "d"
    UPLOAD = "u"

    @classmethod
    def is_download(cls, action):
        return cls._is(action, cls.DOWNLOAD)

    @classmethod
    def is_upload(cls, action):
        return cls._is(action, cls.UPLOAD)

    @staticmethod
    def _is(key, parameter_key):
        return key.lower().startswith(parameter_key.lower())


class ParameterKeys(Enum):
    action = "action"
    path = "path"
    offset = "offset"
    size = "size"
    encoding = "encoding"
    append = "append"
    data = "data"

    @classmethod
    def is_action_parameter(cls, key):
        return cls._is(key, cls.action.value)

    @classmethod
    def is_path_parameter(cls, key):
        return cls._is(key, cls.path.value)

    @classmethod
    def is_offset_parameter(cls, key):
        return cls._is(key, cls.offset.value)

    @classmethod
    def is_size_parameter(cls, key):
        return cls._is(key, cls.size.value)

    @classmethod
    def is_encoding_parameter(cls, key):
        return cls._is(key, cls.encoding.value)

    @classmethod
    def is_append_parameter(cls, key):
        return cls._is(key, cls.append.value)

    @classmethod
    def is_data_parameter(cls, key):
        return cls._is(key, cls.data.value)

    @staticmethod
    def _is(key, parameter_key):
        return key.lower() == parameter_key.lower()
