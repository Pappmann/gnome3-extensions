#!/usr/bin/env python3
"""Helper script to upload the packaged extension to extensions.gnome.org.

The official API for publishing extensions is not publicly documented, but the
community maintained ``gnome-extensions-cli`` project exposes a stable command
line interface that can be used in automation environments.  This wrapper keeps
our workflow declarative and allows us to validate user input before delegating

the heavy lifting to ``gext`` (``gnome-extensions-cli``).
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def ensure_executable(name: str) -> str:
    """Ensure that *name* is available on ``PATH`` and return its absolute path."""
    executable = shutil.which(name)
    if not executable:
        raise FileNotFoundError(
            f"Required executable '{name}' was not found on PATH."
        )
    return executable


def publish_extension(archive: Path, uuid: str, api_key: str, version: str) -> None:
    """Publish *archive* to extensions.gnome.org using ``gext``."""
    gext = ensure_executable("gext")

    subprocess.run([gext, "--help"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    print(f"Publishing {archive.name} for {uuid} (version {version}) via gext…", flush=True)

    publish_cmd = [
        gext,
        "publish",
        str(archive),
        "--api-key",
        api_key,
    ]

    result = subprocess.run(publish_cmd, check=True, capture_output=True, text=True)
    sys.stdout.write(result.stdout)
    sys.stderr.write(result.stderr)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", required=True, type=Path, help="Path to the packaged extension archive")
    parser.add_argument("--uuid", required=True, help="Extension UUID")
    parser.add_argument("--api-key", required=True, help="API key for extensions.gnome.org")
    parser.add_argument("--version", required=True, help="Extension version")

    args = parser.parse_args(argv)

    archive: Path = args.archive
    if not archive.exists():
        parser.error(f"Archive '{archive}' does not exist")

    api_key = args.api_key.strip()
    if not api_key:
        parser.error("The API key must not be empty")

    publish_extension(archive=archive, uuid=args.uuid, api_key=api_key, version=args.version)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
