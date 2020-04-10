from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import logging
import os
from functools import partial

from .constants import Headers, Actions, ContentType
from .request import RequestInfo
from .parameters import Parameters

logger = logging.getLogger(__name__)


class FileHttpServer(ThreadingHTTPServer):

    def __init__(self, address, port, directory):
        super().__init__(
            (address, port),
            partial(FileRequestHandler, directory=directory)
        )


class FileRequestHandler(SimpleHTTPRequestHandler):

    def do_GET(self):
        self._handle_request()

    def do_POST(self):
        self._handle_request()

    def do_HEAD(self):
        self._handle_request()

    def do_PUT(self):
        self._handle_request()

    def _handle_request(self):
        logger.debug(
            '%s -- [%s] "%s"',
            self.address_string(),
            self.log_date_time_string(),
            self.requestline
        )
        request_info = RequestInfo.from_request_handler(self)
        parameters = self.parse_parameters(request_info)
        self.execute(parameters)

    def parse_parameters(self, request_info):
        parameters = Parameters.from_request(request_info)
        parameters.path = self.translate_path(parameters.path)
        return parameters

    def execute(self, parameters):
        try:
            self.execute_action(parameters)
        except FileNotFoundError as ex:
            logger.debug("File not found: %s", ex)
            self.send_error(404)
        except IsADirectoryError as ex:
            logger.debug("Directory requested: %s", ex)
            self.send_error(404)

    def execute_action(self, parameters):
        if os.path.isdir(parameters.path):
            self.execute_dir_action(parameters)
        else:
            self.execute_file_action(parameters)

    def execute_file_action(self, parameters):
        if parameters.action == Actions.DOWNLOAD_FILE:
            self.download_file(parameters)
        elif parameters.action == Actions.UPLOAD_FILE:
            self.upload_file(parameters)

    def download_file(self, parameters):
        data = self.read_file(
            parameters.path,
            parameters.offset,
            parameters.size,
            parameters.encoder
        )
        self.send_response(200)
        self.send_header(Headers.CONTENT_TYPE, ContentType.OCTET_STREAM)
        self.end_headers()
        self.wfile.write(data)

    def upload_file(self, parameters):
        self.write_file_and_dirs(
            parameters.path,
            parameters.data,
            parameters.append,
            parameters.encoder
        )
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

    def execute_dir_action(self, parameters):
        if parameters.action == Actions.DOWNLOAD_FILE:
            directory_bytes = self.list_directory(parameters.path)
            self.wfile.write(directory_bytes.getvalue())
        else:
            raise IsADirectoryError(parameters.path)
