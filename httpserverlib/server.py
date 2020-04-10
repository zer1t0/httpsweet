from http.server import ThreadingHTTPServer
from functools import partial
from .handler import FileRequestHandler


class FileHttpServer(ThreadingHTTPServer):
    """Server to transfer files"""

    def __init__(self, address, port, directory, allow_dir_list):
        super().__init__(
            (address, port),
            partial(
                FileRequestHandler,
                directory=directory,
                allow_dir_list=allow_dir_list,
            )
        )
