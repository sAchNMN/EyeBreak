import app.timer as timer_module
from app.config import AppConfig
from app.state import AppState
from app.timer import ReminderTimer, format_seconds


class FakeFloatingCountdown:
    def __init__(self, should_update: bool = True) -> None:
        self.should_update = should_update
        self.enabled_values: list[bool] = []
        self.paused_values: list[bool] = []
        self.idle_values: list[bool] = []
        self.fullscreen_values: list[bool] = []

    def set_enabled(self, is_enabled: bool) -> None:
        self.enabled_values.append(is_enabled)

    def set_paused(self, is_paused: bool) -> None:
        self.paused_values.append(is_paused)

    def set_idle(self, is_idle: bool) -> None:
        self.idle_values.append(is_idle)

    def set_fullscreen(self, is_fullscreen: bool) -> None:
        self.fullscreen_values.append(is_fullscreen)

    def should_update_display(self) -> bool:
        return self.should_update


class FakeLabel:
    def __init__(self) -> None:
        self.configure_calls: list[dict[str, str]] = []

    def configure(self, **kwargs: str) -> None:
        self.configure_calls.append(kwargs)


class FakeSettingsWindow:
    def __init__(self) -> None:
        self.focus_calls = 0
        self.root = self

    def winfo_exists(self) -> bool:
        return True

    def focus(self) -> None:
        self.focus_calls += 1


def test_format_seconds_rounds_up_remaining_time() -> None:
    assert format_seconds(59.1) == "01:00"
    assert format_seconds(60) == "01:00"
    assert format_seconds(61) == "01:01"


def test_format_seconds_clamps_negative_time() -> None:
    assert format_seconds(-1) == "00:00"


def test_timer_uses_floating_countdown_window() -> None:
    timer = ReminderTimer(AppConfig(), AppState())

    assert timer.countdown_window is None
    assert timer_module.FloatingCountdownWindow.__name__ == "FloatingCountdownWindow"


def test_toggle_floating_countdown_updates_state_and_window() -> None:
    state = AppState()
    timer = ReminderTimer(AppConfig(), state)
    fake_window = FakeFloatingCountdown()
    timer.countdown_window = fake_window  # type: ignore[assignment]

    timer._toggle_floating_countdown()
    timer._toggle_floating_countdown()

    assert state.floating_countdown_enabled is True
    assert fake_window.enabled_values == [False, True]


def test_hidden_floating_countdown_skips_label_update() -> None:
    state = AppState(next_reminder_at=70)
    timer = ReminderTimer(AppConfig(), state)
    fake_window = FakeFloatingCountdown(should_update=False)
    fake_label = FakeLabel()
    timer.countdown_window = fake_window  # type: ignore[assignment]
    timer.status_label = fake_label  # type: ignore[assignment]

    timer._update_countdown_display(now=10)

    assert fake_label.configure_calls == []
    assert fake_window.paused_values == []


def test_visible_floating_countdown_refreshes_label_immediately() -> None:
    state = AppState(next_reminder_at=70)
    timer = ReminderTimer(AppConfig(), state)
    fake_window = FakeFloatingCountdown(should_update=True)
    fake_label = FakeLabel()
    timer.countdown_window = fake_window  # type: ignore[assignment]
    timer.status_label = fake_label  # type: ignore[assignment]

    timer._update_countdown_display(now=10)

    assert fake_window.paused_values == [False]
    assert fake_label.configure_calls == [{"text": "01:00", "fg": "#f9fafb"}]


def test_idle_display_shows_dashes_and_gray_status() -> None:
    state = AppState(next_reminder_at=70)
    timer = ReminderTimer(AppConfig(idle_threshold_minutes=5), state)
    timer._was_idle = True
    fake_window = FakeFloatingCountdown(should_update=True)
    fake_label = FakeLabel()
    timer.countdown_window = fake_window  # type: ignore[assignment]
    timer.status_label = fake_label  # type: ignore[assignment]

    timer._update_countdown_display(now=10)

    assert fake_window.idle_values == [True]
    assert fake_label.configure_calls == [{"text": "--:--", "fg": "#9ca3af"}]


def test_fullscreen_display_shows_dashes_and_blue_status() -> None:
    state = AppState(next_reminder_at=70)
    timer = ReminderTimer(AppConfig(), state)
    timer._was_fullscreen = True
    fake_window = FakeFloatingCountdown(should_update=True)
    fake_label = FakeLabel()
    timer.countdown_window = fake_window  # type: ignore[assignment]
    timer.status_label = fake_label  # type: ignore[assignment]

    timer._update_countdown_display(now=10)

    assert fake_window.fullscreen_values == [True]
    assert fake_label.configure_calls == [{"text": "--:--", "fg": "#60a5fa"}]


def test_handle_fullscreen_state_suppresses_reminder(monkeypatch) -> None:
    timer = ReminderTimer(AppConfig(fullscreen_detection_enabled=True), AppState())
    fake_window = FakeFloatingCountdown()
    timer.countdown_window = fake_window  # type: ignore[assignment]
    monkeypatch.setattr(timer_module, "is_foreground_window_fullscreen", lambda: True)

    assert timer._handle_fullscreen_state() is True
    assert timer._was_fullscreen is True
    assert fake_window.fullscreen_values == [True]


def test_handle_fullscreen_exit_restarts_reminder(monkeypatch) -> None:
    state = AppState(next_reminder_at=0)
    timer = ReminderTimer(AppConfig(reminder_interval_minutes=10), state)
    timer._was_fullscreen = True
    fake_window = FakeFloatingCountdown()
    timer.countdown_window = fake_window  # type: ignore[assignment]
    monkeypatch.setattr(timer_module, "is_foreground_window_fullscreen", lambda: False)
    monkeypatch.setattr(timer_module.time, "monotonic", lambda: 100.0)

    assert timer._handle_fullscreen_state() is False
    assert timer._was_fullscreen is False
    assert state.next_reminder_at == 700.0
    assert fake_window.fullscreen_values == [False]


def test_disabled_fullscreen_detection_does_not_suppress_reminder(monkeypatch) -> None:
    timer = ReminderTimer(AppConfig(fullscreen_detection_enabled=False), AppState())
    monkeypatch.setattr(timer_module, "is_foreground_window_fullscreen", lambda: True)

    assert timer._handle_fullscreen_state() is False
    assert timer._was_fullscreen is False


def test_save_settings_updates_config_and_next_reminder(monkeypatch) -> None:
    saved_configs: list[AppConfig] = []
    state = AppState(next_reminder_at=0)
    timer = ReminderTimer(AppConfig(reminder_interval_minutes=25), state)

    monkeypatch.setattr(timer_module, "save_config", saved_configs.append)
    monkeypatch.setattr(timer_module.time, "monotonic", lambda: 100.0)

    timer._save_settings(AppConfig(reminder_interval_minutes=10))

    assert timer.config.reminder_interval_minutes == 10
    assert saved_configs == [AppConfig(reminder_interval_minutes=10)]
    assert state.next_reminder_at == 700.0


def test_save_settings_keeps_pause_deadline_and_updates_following_reminder(
    monkeypatch,
) -> None:
    state = AppState(paused_until=200.0, next_reminder_at=0)
    timer = ReminderTimer(AppConfig(reminder_interval_minutes=25), state)

    monkeypatch.setattr(timer_module, "save_config", lambda config: None)
    monkeypatch.setattr(timer_module.time, "monotonic", lambda: 100.0)

    timer._save_settings(AppConfig(reminder_interval_minutes=10))

    assert state.paused_until == 200.0
    assert state.next_reminder_at == 800.0


def test_open_settings_focuses_existing_window() -> None:
    timer = ReminderTimer(AppConfig(), AppState())
    fake_settings = FakeSettingsWindow()
    timer.root = object()  # type: ignore[assignment]
    timer.settings_window = fake_settings  # type: ignore[assignment]

    timer._open_settings()

    assert fake_settings.focus_calls == 1
