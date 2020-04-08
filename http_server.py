#!/usr/bin/env python3
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import base64
import logging
import argparse
import os
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

DEFAULT_PORT = 8000
DEFAULT_ADDRESS = "0.0.0.0"


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

    httpd = HTTPServer(
        (address, port),
        CustomHttpRequestHandler
    )
    print("Serving HTTP on {0} port {1} (http://{0}:{1}/) ...".format(
        address, port
    ))

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("Keyboard interrupt received, exiting.")
        httpd.shutdown()
    finally:
        httpd.server_close()

    logging.info('Stop\n')


class CustomHttpRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        logging.debug("GET")
        self._handle_request()

    def do_POST(self):
        logging.debug("POST")
        self._handle_request()

    def _handle_request(self):
        request_info = RequestInfo(
            method=self.command,
            url=self.path
        )

    def execute_action(self, parameters):
        if parameters.action == "download_file":
            self.download_file(
                parameters.path,
                parameters.offset,
                parameters.size,
                EncoderFactory.create(parameters.encoding)
            )
        elif parameters.action == "upload_file":
            self.upload_file(
                parameters.path,
                parameters.data,
                parameters.append,
                EncoderFactory.create(parameters.encoding)
            )

    def download_file(self, path, offset, size, encoder):
        try:
            self.wfile.write(self.read_file(path, offset, size, encoder))
            self.send_response(200)
            self.send_header("Content-type", "application/octet-stream")
            self.end_headers()
        except FileNotFoundError as ex:
            logger.debug("File not found: %s", ex)
            self.send_error(404)

    def upload_file(self, path, data, append, encoder):
        try:
            self.write_file(path, data, append, encoder)
            self.send_response(200)
            self.end_headers()
        except FileNotFoundError as ex:
            logger.debug("File not found: %s", ex)
            self.send_error(404)

    def read_file(self, path, offset, size, encoder):
        with open(path, "rb") as f:
            f.seek(offset)
            return encoder.encode(f.read(size))

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

    def _handle_post(self, url):

        if url.action == "af":
            logging.debug("Appending to file")
            self.append_raw_data_to_file(url)
        elif url.path == "/b64" or url.action == "b64":
            logging.debug("Appending to file base64")
            self.append_base64_data_to_file(url)
        else:
            logging.debug("Show content")
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            print(post_data)

        self.send_response(200)
        self.end_headers()

    def append_base64_data_to_file(self, url):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        file_name = os.path.basename(url.args["file"][0])

        raw_data = base64.b64decode(post_data)

        self.append_data_to_file(file_name, raw_data)

    def append_raw_data_to_file(self, url):
        content_length = int(self.headers['Content-Length'])
        raw_data = self.rfile.read(content_length)
        file_name = os.path.basename(url.args["file"][0])
        self.append_data_to_file(file_name, raw_data)

    def append_data_to_file(self, filename, data):
        with open(filename, "ab") as f:
            f.write(data)


class RequestInfo(object):

    def __init__(self, method, url):
        self.method = method
        self.url = Url(url)


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
        return parse_qs(self._url.query)


class Parameters:

    def __init__(
            self,
            action=None,
            filename=None,
            offset=None,
            size=None,
            encoding=None,
            append=None,
    ):
        self.action = action
        self.filename = filename
        self.offset = offset
        self.size = size
        self.encoding = encoding
        self.append = append

    def update(self, other):
        self.__dict__.update(other.__dict__)


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
