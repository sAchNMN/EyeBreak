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

    def set_enabled(self, is_enabled: bool) -> None:
        self.enabled_values.append(is_enabled)

    def set_paused(self, is_paused: bool) -> None:
        self.paused_values.append(is_paused)

    def set_idle(self, is_idle: bool) -> None:
        self.idle_values.append(is_idle)

    def should_update_display(self) -> bool:
        return self.should_update


class FakeLabel:
    def __init__(self) -> None:
        self.configure_calls: list[dict[str, str]] = []

    def configure(self, **kwargs: str) -> None:
        self.configure_calls.append(kwargs)


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