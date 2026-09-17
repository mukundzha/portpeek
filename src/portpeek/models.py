from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PortRecord:
    """A listening socket and the process that owns it, when available."""

    protocol: str
    address: str
    port: int
    pid: int | None = None
    process: str | None = None
    user: str | None = None

    @property
    def endpoint(self) -> str:
        return f"{self.address}:{self.port}"
