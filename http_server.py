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
            '%s -- [%s] "%s"\n',
            self.address_string(),
            self.log_date_time_string(),
            self.requestline
        )
        request_info = self.parse_request_info()
        print(request_info)
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
        parameters = Parameters.from_method(request_info.method)
        parameters.update(Parameters.from_path(request_info.url.path))
        parameters.update(
            Parameters.from_dictionary(request_info.url.query_string)
        )

        content_length = request_info.content_length
        if content_length > 0:
            content = request_info.rfile.read(content_length)
            if request_info.content_type == ContentType.URLENCODED:
                content_params = Parameters.from_dictionary(
                    parse_qs(content)
                )
            elif request_info.content_type == ContentType.JSON:
                content_params = Parameters.from_dictionary(
                    json.loads(content)
                )
            else:
                content_params = Parameters.from_raw_data(content)

            parameters.update(content_params)

        parameters.path = self.translate_path(parameters.path)

        return parameters

    def execute_action(self, parameters):
        if parameters.action == Actions.DOWNLOAD_FILE:
            self.download_file(
                parameters.path,
                parameters.offset,
                parameters.size,
                EncoderFactory.create(parameters.encoding)
            )
        elif parameters.action == Actions.UPLOAD_FILE:
            self.upload_file(
                parameters.path,
                parameters.data,
                parameters.append,
                EncoderFactory.create(parameters.encoding)
            )

    def download_file(self, path, offset, size, encoder):
        self.wfile.write(self.read_file(path, offset, size, encoder))
        self.send_response(200)
        self.send_header("Content-type", ContentType.OCTET_STREAM)
        self.end_headers()

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


class Url:

    def __init__(self, url_str):
        self._url = urlparse(url_str)
        self._parameters = parse_qs(self._url)

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


class Parameters:

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

    @property
    def is_dir(self):
        return os.path.isdir(self.path)

    def update(self, other):
        for key, value in other.__dict__.items():
            if value is not None:
                self.__dict__[key] = value

    @classmethod
    def from_method(cls, method):
        if method == "POST" or method == "PUT":
            return cls(action=Actions.UPLOAD_FILE)
        else:
            return cls(action=Actions.DOWNLOAD_FILE)

    @classmethod
    def from_path(cls, path):
        return cls(path=path)

    @classmethod
    def from_dictionary(cls, qs):
        append = "append" in qs
        return cls(
            action=qs.get("action", None),
            path=qs.get("path", None),
            offset=qs.get("offset", None),
            size=qs.get("size", None),
            encoding=qs.get("encoding", None),
            append=append,
            data=qs.get("data", None)
        )

    @classmethod
    def from_raw_data(cls, raw_data):
        return cls(data=raw_data)


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
