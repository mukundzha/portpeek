#!/usr/bin/env sh
set -eu

if [ "$(uname -s)" != "Linux" ]; then
    printf '%s\n' 'Portpeek Beta 1 currently supports Linux only.' >&2
    exit 1
fi

python="${PYTHON:-python3}"
if ! command -v "$python" >/dev/null 2>&1; then
    printf 'Python 3.10+ is required; %s was not found.\n' "$python" >&2
    exit 1
fi

if ! "$python" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)'; then
    printf '%s\n' 'Python 3.10 or newer is required.' >&2
    exit 1
fi

install_root="${XDG_DATA_HOME:-$HOME/.local/share}/portpeek"
bin_dir="${HOME}/.local/bin"
venv="${install_root}/venv"

printf 'Installing Portpeek for the current user in %s...\n' "$venv"
mkdir -p "$install_root" "$bin_dir"
"$python" -m venv "$venv"
"$venv/bin/python" -m pip install --no-deps .
ln -sf "$venv/bin/portpeek" "$bin_dir/portpeek"

if ! command -v portpeek >/dev/null 2>&1; then
    printf '%s\n' 'Portpeek installed, but ~/.local/bin is not on PATH.' >&2
    printf 'Add %s to PATH, then run portpeek --version.\n' "$bin_dir"
    "$bin_dir/portpeek" --version
    exit 1
fi

portpeek --version
printf '%s\n' 'Portpeek is ready.'
