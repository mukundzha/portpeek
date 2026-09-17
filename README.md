# Portpeek

Portpeek Beta 1 is a lightweight Linux CLI for inspecting listening TCP ports and the processes that own them.

## Requirements

- Linux x86_64/amd64
- Python 3.10 or newer

Portpeek reads `/proc/net/tcp` and `/proc/net/tcp6`, then maps socket inodes through `/proc/<pid>/fd`. It does not shell out to `netstat` or `lsof`; this keeps the core dependency-free and avoids relying on distribution-specific utilities. Process details can be unavailable when Linux permissions prevent reading another process's descriptors.

## Install

From a checkout:

```sh
./install.sh
```

The installer verifies Linux and Python 3.10+, then installs the package for the current user. Ensure Python's user-local bin directory is on `PATH` if the installer reports that `portpeek` cannot be found.

The normal pip flow is also supported:

```sh
python3 -m pip install --user .
portpeek --version
```

After installation, the command is independent of the current working directory:

```sh
cd /tmp
portpeek
portpeek 3000
```

## Development

```sh
python3 -m pip install -e '.[test]'
python3 -m pytest
python3 -m portpeek --version
```

Beta 1 intentionally supports Linux only. Discovery is behind a small interface so future `macos.py` and `windows.py` backends can be added without changing the CLI contract.
