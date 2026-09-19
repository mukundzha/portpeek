from __future__ import annotations

import argparse
import sys

from . import __version__
from .discovery.base import DiscoveryError
from .discovery.linux import LinuxPortDiscovery
from .output import render


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Show listening TCP ports on Linux.")
    parser.add_argument("port", nargs="?", type=_port_number, help="only show this TCP port")
    parser.add_argument("--version", action="version", version=f"portpeek {__version__}")
    return parser


def _port_number(value: str) -> int:
    port = int(value)
    if not 1 <= port <= 65535:
        raise argparse.ArgumentTypeError("port must be between 1 and 65535")
    return port


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        records = LinuxPortDiscovery().listening_ports()
    except DiscoveryError as exc:
        print(f"portpeek: {exc}", file=sys.stderr)
        return 1
    if args.port is not None:
        records = [record for record in records if record.port == args.port]
        if not records:
            print(render(records, args.port))
            return 1
    print(render(records, args.port))
    return 0
