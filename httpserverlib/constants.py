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
        return action.startswith(cls.DOWNLOAD)

    @classmethod
    def is_upload(cls, action):
        return action.startswith(cls.UPLOAD)


class QueryStringKeys(Enum):
    action = "action"
    path = "path"
    offset = "offset"
    size = "size"
    encoding = "encoding"
    append = "append"
    data = "data"
