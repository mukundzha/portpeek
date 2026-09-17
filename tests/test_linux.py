from pathlib import Path

from portpeek.discovery.linux import LinuxPortDiscovery, _parse_endpoint


def test_parse_ipv4_endpoint() -> None:
    assert _parse_endpoint("0100007F:0BB8", "tcp") == ("127.0.0.1", 3000)


def test_parse_ipv6_endpoint() -> None:
    assert _parse_endpoint("00000000000000000000000000000000:0050", "tcp6") == ("::", 80)


def test_discovery_reads_proc_data_and_owner(tmp_path: Path, monkeypatch) -> None:
    proc_net = tmp_path / "net"
    proc_net.mkdir()
    (proc_net / "tcp").write_text(
        "  sl local_address rem_address st tx_queue rx_queue tr tm->when retrnsmt   uid  timeout inode\n"
        "   0: 0100007F:0BB8 00000000:0000 0A 00000000:00000000 00:00000000 00000000   1000        0 4242 1\n",
        encoding="ascii",
    )
    process = tmp_path / "1234"
    fd_dir = process / "fd"
    fd_dir.mkdir(parents=True)
    (process / "comm").write_text("demo-server\n", encoding="utf-8")
    (process / "status").write_text("Name:\tdemo\nUid:\t1000\t1000\t1000\t1000\n", encoding="utf-8")
    (fd_dir / "3").symlink_to("socket:[4242]")
    monkeypatch.setattr("portpeek.discovery.linux.pwd.getpwuid", lambda uid: type("Entry", (), {"pw_name": "tester"})())

    records = LinuxPortDiscovery(tmp_path).listening_ports()

    assert len(records) == 1
    assert records[0].port == 3000
    assert records[0].address == "127.0.0.1"
    assert records[0].pid == 1234
    assert records[0].process == "demo-server"
    assert records[0].user == "tester"
