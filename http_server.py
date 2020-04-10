#!/usr/bin/env python3
import logging
import argparse
import os
import ssl

from httpserverlib import FileHttpServer

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
        "--dir-list",
        help="Allow list directories from requests",
        action="store_true",
    )

    parser.add_argument(
        "--cert",
        help="Certificate file to deploy an HTTPS server.",
        type=argparse.FileType('r'),
        required=False
    )

    parser.add_argument(
        "--key",
        help="Key file to deploy an HTTPS server. Require provide also --cert",
        type=argparse.FileType('r'),
        required=False
    )

    parser.add_argument(
        "--debug",
        required=False,
        action="store_true"
    )
    args = parser.parse_args()

    if args.key and args.cert is None:
        parser.error("--cert required with --key")

    if args.cert:
        args.cert = args.cert.name

    if args.key:
        args.key = args.key.name

    return args


def main():
    args = parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    port = args.port
    address = args.address
    protocol = "http"

    httpd = FileHttpServer(
        address,
        port,
        args.directory,
        args.dir_list
    )

    if args.cert:
        protocol = "https"
        try:
            httpd.socket = ssl.wrap_socket(
                httpd.socket,
                certfile=args.cert,
                keyfile=args.key,
                server_side=True,
            )
        except ssl.SSLError as ex:
            print("SSL error: {}. "
                  "Check if you provide the correct cert and key".format(ex))
            return
        except OSError as ex:
            print("Error: {}. Maybe certificate password is wrong.".format(ex))
            return

    print(
        "Serving {proto_upper} on {host} port {port} "
        "({proto_lower}://{host}:{port}/) ...".format(
            host=address,
            port=port,
            proto_upper=protocol.upper(),
            proto_lower=protocol.lower()
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
