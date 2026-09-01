import json
from pathlib import Path

import pytest

from app.persistence import atomic_write_json, read_json_object


def test_atomic_write_json_writes_a_complete_payload(tmp_path: Path) -> None:
    target = tmp_path / "config.json"

    atomic_write_json(target, {"reminder_interval_minutes": 25})

    assert json.loads(target.read_text(encoding="utf-8")) == {
        "reminder_interval_minutes": 25
    }
    assert not list(tmp_path.glob(".config.json.*.tmp"))


def test_read_json_object_uses_backup_when_main_file_is_invalid(tmp_path: Path) -> None:
    target = tmp_path / "config.json"
    target.with_name("config.json.bak").write_text(
        '{"reminder_interval_minutes": 25}', encoding="utf-8"
    )
    target.write_text("{broken", encoding="utf-8")

    assert read_json_object(target, {}, backup=True) == {
        "reminder_interval_minutes": 25
    }


def test_read_json_object_returns_default_for_non_object_json(tmp_path: Path) -> None:
    target = tmp_path / "config.json"
    target.write_text("[]", encoding="utf-8")

    assert read_json_object(target, {"fallback": True}) == {"fallback": True}


def test_atomic_write_json_keeps_old_target_when_replace_fails(
    tmp_path: Path, monkeypatch
) -> None:
    target = tmp_path / "config.json"
    target.write_text('{"old": true}', encoding="utf-8")

    def fail_replace(source: str, destination: str) -> None:
        raise OSError("replace failed")

    monkeypatch.setattr("app.persistence.os.replace", fail_replace)

    with pytest.raises(OSError, match="replace failed"):
        atomic_write_json(target, {"new": True})

    assert json.loads(target.read_text(encoding="utf-8")) == {"old": True}
