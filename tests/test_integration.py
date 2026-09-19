import os
import socket

import pytest

from portpeek.discovery.linux import LinuxPortDiscovery


def test_discovery_finds_temporary_listener() -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
        listener.bind(("127.0.0.1", 0))
        listener.listen()
        port = listener.getsockname()[1]
        records = LinuxPortDiscovery().listening_ports()

    matches = [record for record in records if record.port == port and record.address == "127.0.0.1"]
    assert matches
    assert any(record.pid == os.getpid() for record in matches)


def test_discovery_finds_ipv6_listener() -> None:
    try:
        listener = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    except OSError as exc:
        pytest.skip(f"IPv6 unavailable: {exc}")
    with listener:
        try:
            listener.bind(("::1", 0))
            listener.listen()
        except OSError as exc:
            pytest.skip(f"IPv6 unavailable: {exc}")
        port = listener.getsockname()[1]
        records = LinuxPortDiscovery().listening_ports()

    matches = [record for record in records if record.port == port and record.address == "::1"]
    assert matches
    assert matches[0].protocol == "tcp6"
    assert any(record.pid == os.getpid() for record in matches)
