from __future__ import annotations

import json
import logging
import os
import shutil
import tempfile
from pathlib import Path


logger = logging.getLogger(__name__)


def atomic_write_json(
    path: Path, payload: dict[str, object], backup: bool = False
) -> None:
    """Write a JSON object without exposing a partially written target."""
    path = Path(path)
    temporary_path: Path | None = None
    try:
        file_descriptor, temporary_name = tempfile.mkstemp(
            prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
        )
        temporary_path = Path(temporary_name)
        with os.fdopen(file_descriptor, "w", encoding="utf-8") as stream:
            json.dump(payload, stream, ensure_ascii=False, indent=2)
            stream.flush()
            os.fsync(stream.fileno())

        if backup and path.exists():
            shutil.copyfile(path, path.with_name(f"{path.name}.bak"))
        os.replace(temporary_path, path)
        temporary_path = None
    finally:
        if temporary_path is not None:
            try:
                temporary_path.unlink()
            except FileNotFoundError:
                pass


def read_json_object(
    path: Path, default: dict[str, object], backup: bool = False
) -> dict[str, object]:
    """Read a JSON object, optionally falling back to its ``.bak`` file."""
    path = Path(path)
    candidates = [path]
    if backup:
        candidates.append(path.with_name(f"{path.name}.bak"))

    for candidate in candidates:
        try:
            value = json.loads(candidate.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(value, dict):
            return value
        logger.warning("Ignoring non-object JSON in %s", candidate)
    return default
