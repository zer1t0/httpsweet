#!/usr/bin/env python3
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs
import base64
import logging
import argparse
import os
import json
from abc import ABC, abstractmethod
from functools import partial
from enum import Enum

logger = logging.getLogger(__name__)

DEFAULT_PORT = 8000
DEFAULT_ADDRESS = "0.0.0.0"
DEFAULT_DIR = os.getcwd()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "port",
        default=DEFAULT_PORT,
        nargs="?",
        type=int,
        help="Specify alternate port [default: {}]".format(DEFAULT_PORT)
    )
    parser.add_argument(
        "--bind", "-b",
        default=DEFAULT_ADDRESS,
        metavar="ADDRESS",
        dest="address",
        help="Specify alternate bind address [default: {}]".format(
            DEFAULT_ADDRESS
        )
    )

    parser.add_argument(
        "--directory", "-d",
        default=DEFAULT_DIR,
        help="Specify alternative directory [default: {}]".format(
            DEFAULT_DIR
        )
    )

    parser.add_argument(
        "--debug",
        required=False,
        action="store_true"
    )
    return parser.parse_args()


def main():
    args = parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    port = args.port
    address = args.address

    httpd = ThreadingHTTPServer(
        (address, port),
        partial(CustomHttpRequestHandler, directory=args.directory)
    )
    print(
        "Serving HTTP on {host} port {port} (http://{host}:{port}/) ...".format(
            host=address, port=port
        )
    )

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("Keyboard interrupt received, exiting.")
        httpd.shutdown()
    finally:
        httpd.server_close()

    logging.info('Stop\n')


class CustomHttpRequestHandler(SimpleHTTPRequestHandler):

    def do_GET(self):
        logging.debug("GET")
        self._handle_request()

    def do_POST(self):
        logging.debug("POST")
        self._handle_request()

    def do_HEAD(self):
        logging.debug("HEAD")
        self._handle_request()

    def do_PUT(self):
        logging.debug("%s PUT")
        self._handle_request()

    def _handle_request(self):
        logger.debug(
            '%s -- [%s] "%s"',
            self.address_string(),
            self.log_date_time_string(),
            self.requestline
        )
        request_info = self.parse_request_info()
        parameters = self.parse_parameters(request_info)

        try:
            self.execute_action(parameters)
        except FileNotFoundError as ex:
            logger.debug("File not found: %s", ex)
            self.send_error(404)
        except IsADirectoryError as ex:
            logger.debug("Directory requested: %s", ex)
            self.send_error(404)

    def parse_request_info(self):
        return RequestInfo(
            method=self.command,
            url=self.path,
            headers=self.headers,
            rfile=self.rfile
        )

    def parse_parameters(self, request_info):
        builder = ParametersBuilder()
        builder.update_from_method(request_info.method)
        builder.update_from_path(request_info.path)
        builder.update_from_query_string(request_info.url.query_string)

        content_length = request_info.content_length
        if content_length > 0:
            content = request_info.rfile.read(content_length)
            if request_info.content_type == ContentType.URLENCODED:
                builder.update_from_query_string((parse_qs(content)))
            elif request_info.content_type == ContentType.JSON:
                builder.update_from_dictionary(json.loads(content))
            else:
                builder.update_from_raw_data(content)

        parameters = builder.build()
        parameters.path = self.translate_path(parameters.path)

        return parameters

    def execute_action(self, parameters):
        if parameters.action == Actions.DOWNLOAD_FILE:
            self.download_file(
                parameters.path,
                parameters.offset,
                parameters.size,
                parameters.encoder
            )
        elif parameters.action == Actions.UPLOAD_FILE:
            self.upload_file(
                parameters.path,
                parameters.data,
                parameters.append,
                parameters.encoder
            )

    def download_file(self, path, offset, size, encoder):
        data = self.read_file(path, offset, size, encoder)
        self.send_response(200)
        self.send_header("Content-type", ContentType.OCTET_STREAM)
        self.end_headers()
        self.wfile.write(data)

    def upload_file(self, path, data, append, encoder):
        self.write_file_and_dirs(path, data, append, encoder)
        self.send_response(200)
        self.end_headers()

    def read_file(self, path, offset, size, encoder):
        with open(path, "rb") as f:
            f.seek(offset)
            return encoder.encode(f.read(size))

    def write_file_and_dirs(self, path, data, append, encoder):
        try:
            self.write_file(path, data, append, encoder)
        except FileNotFoundError:
            self.create_dirs(path)
            self.write_file(path, data, append, encoder)

    def create_dirs(self, path):
        dir_path = os.path.dirname(path)
        os.makedirs(dir_path)

    def write_file(self, path, data, append, encoder):
        mode = "ab" if append else "wb"
        with open(path, mode) as f:
            f.write(encoder.decode(data))

    def _handle_get(self, url):
        path = url.path[1:]
        try:
            f = open(path, "rb")

            self.send_response(200)
            self.send_header("Content-type", "application/octet-stream")
            self.end_headers()
            self.wfile.write(f.read())

            f.close()
        except IOError:
            self.send_error(404)


class ContentType:
    JSON = "application/json"
    URLENCODED = "application/x-www-form-urlencoded"
    OCTET_STREAM = "application/octet-stream"


class RequestInfo(object):

    def __init__(self, method, url, headers, rfile):
        self.method = method
        self.url = Url(url)
        self.headers = headers
        self.rfile = rfile

    @property
    def content_type(self):
        return self.headers.get("Content-type", "")

    @property
    def content_length(self):
        return int(self.headers.get("Conten-Length", "0"))

    @property
    def path(self):
        return self.url.path


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
                d[key] = qs[key][0]
            else:
                d[key] = None

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


class EncoderFactory(object):

    @classmethod
    def create(cls, encoding):
        if encoding == "64":
            return Base64Encoder()
        else:
            return EmptyEncoder()


class Encoder(ABC):

    @abstractmethod
    def encode(self, data):
        raise NotImplementedError()

    @abstractmethod
    def decode(self, data):
        raise NotImplementedError()


class EmptyEncoder(Encoder):

    def encode(self, data):
        return data

    def decode(self, data):
        return data


class Base64Encoder(Encoder):

    def encode(self, data):
        return base64.b64encode(data)

    def decode(self, data):
        return base64.b64decode(data)


if __name__ == '__main__':
    main()
