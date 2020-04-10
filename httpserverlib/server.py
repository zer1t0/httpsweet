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
        parameters = Parameters.from_request(request_info)

        ActionHandler(
            path=self.translate_path(parameters.path),
            parameters=parameters,
            request_handler=self
        ).execute()


class ActionHandler(object):

    def __init__(self, path, parameters, request_handler):
        self.path = path
        self.parameters = parameters
        self.request_handler = request_handler

    def execute(self):
        try:
            self.execute_action()
        except FileNotFoundError as ex:
            logger.debug("File not found: %s", ex)
            self.send_error(404)
        except IsADirectoryError as ex:
            logger.debug("Directory requested: %s", ex)
            self.send_error(404)

    def execute_action(self):
        if os.path.isdir(self.path):
            self.execute_dir_action()
        else:
            self.execute_file_action()

    def execute_file_action(self):
        if self.action == Actions.DOWNLOAD_FILE:
            self.download_file()
        elif self.action == Actions.UPLOAD_FILE:
            self.upload_file()

    def download_file(self):
        data = self.read_file(self.path, self.offset, self.size, self.encoder)
        self.send_response(200)
        self.send_header(Headers.CONTENT_TYPE, ContentType.OCTET_STREAM)
        self.end_headers()
        self.write(data)

    def upload_file(self):
        self.write_file_and_dirs(
            self.path,
            self.data,
            self.append,
            self.encoder
        )
        self.send_response(200)
        self.end_headers()

    def execute_dir_action(self):
        if self.action == Actions.DOWNLOAD_FILE:
            directory_bytes = self.list_directory()
            self.write(directory_bytes)
        else:
            raise IsADirectoryError(self.path)

    @property
    def action(self):
        return self.parameters.action

    @property
    def offset(self):
        return self.parameters.offset

    @property
    def size(self):
        return self.parameters.size

    @property
    def encoder(self):
        return self.parameters.encoder

    @property
    def append(self):
        return self.parameters.append

    @property
    def data(self):
        return self.parameters.data

    def send_error(self, code):
        self.request_handler.send_error(code)

    def send_response(self, code):
        self.request_handler.send_response(code)

    def send_header(self, name, value):
        self.request_handler.send_header(name, value)

    def end_headers(self):
        self.request_handler.end_headers()

    def write(self, data):
        self.request_handler.wfile.write(data)

    def list_directory(self):
        return self.request_handler.list_directory(self.path).getvalue()

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
