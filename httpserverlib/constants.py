from enum import Enum


class ContentType:
    JSON = "application/json"
    URLENCODED = "application/x-www-form-urlencoded"
    OCTET_STREAM = "application/octet-stream"


class Headers:
    CONTENT_TYPE = "Content-Type"
    CONTENT_LENGTH = "Content-Length"


class Actions:
    DOWNLOAD_FILE = "download_file"
    UPLOAD_FILE = "upload_file"


class QueryStringKeys(Enum):
    action = "action"
    path = "path"
    offset = "offset"
    size = "size"
    encoding = "encoding"
    append = "append"
    data = "data"
