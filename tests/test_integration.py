import socket

from portpeek.discovery.linux import LinuxPortDiscovery


def test_discovery_finds_temporary_listener() -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
        listener.bind(("127.0.0.1", 0))
        listener.listen()
        port = listener.getsockname()[1]
        records = LinuxPortDiscovery().listening_ports()

    matches = [record for record in records if record.port == port and record.address == "127.0.0.1"]
    assert matches
    assert any(record.pid == __import__("os").getpid() for record in matches)
