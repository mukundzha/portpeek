from __future__ import annotations

import ipaddress
import os
import pwd
from pathlib import Path

from portpeek.models import PortRecord

from .base import DiscoveryError, PortDiscovery


class LinuxPortDiscovery(PortDiscovery):
    """Discover TCP listeners through Linux procfs interfaces."""

    def __init__(self, proc_root: Path = Path("/proc")) -> None:
        self.proc_root = proc_root

    def listening_ports(self) -> list[PortRecord]:
        owners = self._socket_owners()
        records: list[PortRecord] = []
        for filename, protocol in (("net/tcp", "tcp"), ("net/tcp6", "tcp6")):
            path = self.proc_root / filename
            try:
                lines = path.read_text(encoding="ascii").splitlines()[1:]
            except FileNotFoundError:
                continue
            except OSError as exc:
                raise DiscoveryError(f"cannot read {path}: {exc}") from exc
            for line in lines:
                fields = line.split()
                if len(fields) < 10 or fields[3] != "0A":
                    continue
                address, port = _parse_endpoint(fields[1], protocol)
                inode = fields[9]
                pid, process, user = owners.get(inode, (None, None, None))
                records.append(PortRecord(protocol, address, port, pid, process, user))
        return sorted(records, key=lambda item: (item.port, item.protocol, item.address))

    def _socket_owners(self) -> dict[str, tuple[int | None, str | None, str | None]]:
        owners: dict[str, tuple[int | None, str | None, str | None]] = {}
        try:
            process_dirs = list(self.proc_root.iterdir())
        except OSError as exc:
            raise DiscoveryError(f"cannot inspect {self.proc_root}: {exc}") from exc

        for process_dir in process_dirs:
            if not process_dir.name.isdigit():
                continue
            pid = int(process_dir.name)
            process = _read_process_name(process_dir)
            user = _read_process_user(process_dir)
            fd_dir = process_dir / "fd"
            try:
                descriptors = list(fd_dir.iterdir())
            except OSError:
                continue
            for descriptor in descriptors:
                try:
                    target = os.readlink(descriptor)
                except OSError:
                    continue
                if not target.startswith("socket:[") or not target.endswith("]"):
                    continue
                inode = target[8:-1]
                owners.setdefault(inode, (pid, process, user))
        return owners


def _parse_endpoint(value: str, protocol: str) -> tuple[str, int]:
    address_hex, port_hex = value.split(":")
    port = int(port_hex, 16)
    if protocol == "tcp":
        octets = [str(int(address_hex[index : index + 2], 16)) for index in range(0, 8, 2)]
        return ".".join(reversed(octets)), port

    raw = bytes.fromhex(address_hex)
    network_bytes = b"".join(raw[index : index + 4][::-1] for index in range(0, 16, 4))
    return ipaddress.IPv6Address(network_bytes).compressed, port


def _read_process_name(process_dir: Path) -> str | None:
    try:
        name = (process_dir / "comm").read_text(encoding="utf-8").strip()
    except OSError:
        return None
    return name or None


def _read_process_user(process_dir: Path) -> str | None:
    try:
        uid = (process_dir / "status").read_text(encoding="utf-8")
    except OSError:
        return None
    for line in uid.splitlines():
        if line.startswith("Uid:"):
            try:
                return pwd.getpwuid(int(line.split()[1])).pw_name
            except (IndexError, ValueError, KeyError):
                return str(line.split()[1]) if len(line.split()) > 1 else None
    return None
