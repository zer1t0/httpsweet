#!/usr/bin/env python3
import logging
import argparse
import os

from httpserverlib import FileHttpServer

logger = logging.getLogger(__name__)

DEFAULT_PORT = 8000
DEFAULT_ADDRESS = "0.0.0.0"
DEFAULT_DIR = os.getcwd()

# TODO : list directory, if enable
# TODO : allow use certificate
# TODO : refactor code


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
        "--list-dir",
        help="Allow list directories from requests",
        action="store_true",
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

    httpd = FileHttpServer(
        address,
        port,
        args.directory,
        args.list_dir
    )
    print(
        "Serving HTTP on {host} port {port} "
        "(http://{host}:{port}/) ...".format(
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


if __name__ == '__main__':
    main()
