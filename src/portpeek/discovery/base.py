from abc import ABC, abstractmethod

from portpeek.models import PortRecord


class DiscoveryError(RuntimeError):
    """Raised when the operating system cannot provide port information."""


class PortDiscovery(ABC):
    """Interface implemented by each supported operating system."""

    @abstractmethod
    def listening_ports(self) -> list[PortRecord]:
        """Return currently listening TCP sockets."""
