from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import logging
import os
from functools import partial

from .constants import Headers, Actions, ContentType
from .request import RequestInfo
from .parameters import ParametersBuilder

logger = logging.getLogger(__name__)


class FileHttpServer(ThreadingHTTPServer):

    def __init__(self, address, port, directory):
        super().__init__(
            (address, port),
            partial(FileRequestHandler, directory=directory)
        )


class FileRequestHandler(SimpleHTTPRequestHandler):

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
        parameters = ParametersBuilder.from_request(request_info).build()
        parameters.path = self.translate_path(parameters.path)

        return parameters

    def execute_action(self, parameters):
        print(repr(parameters))
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
        self.send_header(Headers.CONTENT_TYPE, ContentType.OCTET_STREAM)
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




