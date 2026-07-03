from __future__ import annotations

from collections.abc import Callable

import pystray

from app.autostart import is_autostart_enabled
from app.icons import create_icon_image


PAUSE_OPTIONS_MINUTES = (5, 15, 30, 60, 120)


class TrayIcon:
    def __init__(
        self,
        on_break_now: Callable[[], None],
        on_pause: Callable[[int], None],
        on_resume: Callable[[], None],
        on_toggle_floating: Callable[[], None],
        on_toggle_autostart: Callable[[], None],
        on_exit: Callable[[], None],
    ) -> None:
        self.icon = pystray.Icon(
            "EyeBreak",
            create_icon_image(),
            "EyeBreak",
            pystray.Menu(
                pystray.MenuItem("立即休息", lambda icon, item: on_break_now()),
                pystray.MenuItem("暂停", _pause_menu(on_pause)),
                pystray.MenuItem("恢复", lambda icon, item: on_resume()),
                pystray.MenuItem("开关悬浮窗", _toggle_floating_action(on_toggle_floating)),
                pystray.MenuItem(
                    "开机自启",
                    _autostart_toggle_action(on_toggle_autostart),
                    checked=lambda item: is_autostart_enabled(),
                ),
                pystray.MenuItem("退出", lambda icon, item: on_exit()),
            ),
        )

    def start(self) -> None:
        self.icon.run_detached()

    def stop(self) -> None:
        self.icon.stop()


def _pause_menu(on_pause: Callable[[int], None]) -> pystray.Menu:
    return pystray.Menu(
        *(
            pystray.MenuItem(
                _format_pause_label(minutes),
                _pause_action(on_pause, minutes),
            )
            for minutes in PAUSE_OPTIONS_MINUTES
        )
    )


def _pause_action(
    on_pause: Callable[[int], None],
    minutes: int,
) -> Callable[[pystray.Icon, pystray.MenuItem], None]:
    def action(icon: pystray.Icon, item: pystray.MenuItem) -> None:
        on_pause(minutes)

    return action


def _toggle_floating_action(
    on_toggle_floating: Callable[[], None],
) -> Callable[[pystray.Icon, pystray.MenuItem], None]:
    def action(icon: pystray.Icon, item: pystray.MenuItem) -> None:
        on_toggle_floating()

    return action


def _autostart_toggle_action(
    on_toggle_autostart: Callable[[], None],
) -> Callable[[pystray.Icon, pystray.MenuItem], None]:
    def action(icon: pystray.Icon, item: pystray.MenuItem) -> None:
        on_toggle_autostart()

    return action


def _format_pause_label(minutes: int) -> str:
    if minutes >= 60 and minutes % 60 == 0:
        return f"{minutes // 60}小时"
    return f"{minutes}分钟"