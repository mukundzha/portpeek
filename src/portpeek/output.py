from collections.abc import Iterable

from portpeek.models import PortRecord


def render(records: Iterable[PortRecord], selected_port: int | None = None) -> str:
    records = list(records)
    if not records:
        if selected_port is None:
            return "No listening TCP ports found."
        return f"No listening TCP process found on port {selected_port}."

    headers = ("PORT", "ADDRESS", "PROTOCOL", "PID", "PROCESS", "USER")
    rows = [
        (
            str(record.port),
            record.address,
            record.protocol,
            str(record.pid or "-"),
            record.process or "-",
            record.user or "-",
        )
        for record in records
    ]
    widths = [max(len(header), *(len(row[index]) for row in rows)) for index, header in enumerate(headers)]
    lines = ["  ".join(value.ljust(widths[index]) for index, value in enumerate(headers))]
    lines.append("  ".join("-" * width for width in widths))
    lines.extend("  ".join(value.ljust(widths[index]) for index, value in enumerate(row)) for row in rows)
    return "\n".join(lines)
