from portpeek.cli import main
from portpeek.models import PortRecord


def test_cli_filters_by_port(monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        "portpeek.cli.LinuxPortDiscovery.listening_ports",
        lambda self: [PortRecord("tcp", "127.0.0.1", 3000, 42, "python", "tester")],
    )

    assert main(["3000"]) == 0
    assert "3000" in capsys.readouterr().out


def test_cli_rejects_invalid_port(capsys) -> None:
    try:
        main(["70000"])
    except SystemExit as exc:
        assert exc.code == 2
    assert "port must be between" in capsys.readouterr().err
