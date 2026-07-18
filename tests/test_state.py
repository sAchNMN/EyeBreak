import json

from app.state import APP_STATE_PATH, AppState, load_app_state, save_app_state


def test_default_app_state_path_is_absolute() -> None:
    assert APP_STATE_PATH.is_absolute()


def test_load_app_state_restores_floating_settings(tmp_path) -> None:
    state_path = tmp_path / "app_state.json"
    state_path.write_text(
        json.dumps(
            {
                "floating_countdown": {
                    "enabled": False,
                    "edge": None,
                    "x": 320,
                    "y": 180,
                }
            }
        ),
        encoding="utf-8",
    )

    state = load_app_state(state_path)

    assert state.floating_countdown_enabled is False
    assert state.floating_countdown_edge is None
    assert state.floating_countdown_x == 320
    assert state.floating_countdown_y == 180


def test_load_app_state_defaults_missing_floating_enabled_flag(tmp_path) -> None:
    state_path = tmp_path / "app_state.json"
    state_path.write_text(
        json.dumps({"floating_countdown": {"edge": "right", "x": 0, "y": 1}}),
        encoding="utf-8",
    )

    assert load_app_state(state_path).floating_countdown_enabled is True


def test_load_app_state_falls_back_for_invalid_file(tmp_path) -> None:
    state_path = tmp_path / "app_state.json"
    state_path.write_text("{bad json", encoding="utf-8")

    assert load_app_state(state_path) == AppState()


def test_save_app_state_writes_persistent_floating_state(tmp_path) -> None:
    state_path = tmp_path / "app_state.json"
    state = AppState(
        is_running=False,
        paused_until=123,
        next_reminder_at=456,
        floating_countdown_enabled=False,
        floating_countdown_edge="bottom",
        floating_countdown_x=500,
        floating_countdown_y=900,
    )

    save_app_state(state, state_path)

    assert json.loads(state_path.read_text(encoding="utf-8")) == {
        "floating_countdown": {
            "enabled": False,
            "edge": "bottom",
            "x": 500,
            "y": 900,
        }
    }


def test_save_app_state_ignores_write_failure(monkeypatch) -> None:
    def raise_permission_error(self, data, encoding=None):
        raise PermissionError

    monkeypatch.setattr("pathlib.Path.write_text", raise_permission_error)

    save_app_state(AppState())