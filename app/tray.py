from __future__ import annotations

from collections.abc import Callable

import pystray
from PIL import Image, ImageDraw


PAUSE_OPTIONS_MINUTES = (5, 15, 30, 60, 120)


class TrayIcon:
    def __init__(
        self,
        on_break_now: Callable[[], None],
        on_pause: Callable[[int], None],
        on_resume: Callable[[], None],
        on_exit: Callable[[], None],
    ) -> None:
        self.icon = pystray.Icon(
            "EyeBreak",
            _create_icon_image(),
            "EyeBreak",
            pystray.Menu(
                pystray.MenuItem("立即休息", lambda icon, item: on_break_now()),
                pystray.MenuItem("暂停", _pause_menu(on_pause)),
                pystray.MenuItem("恢复", lambda icon, item: on_resume()),
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


def _format_pause_label(minutes: int) -> str:
    if minutes >= 60 and minutes % 60 == 0:
        return f"{minutes // 60}小时"
    return f"{minutes}分钟"


def _create_icon_image() -> Image.Image:
    image = Image.new("RGBA", (64, 64), (17, 24, 39, 255))
    draw = ImageDraw.Draw(image)
    draw.ellipse((10, 18, 54, 46), fill=(249, 250, 251, 255))
    draw.ellipse((23, 22, 41, 40), fill=(34, 197, 94, 255))
    draw.ellipse((29, 28, 35, 34), fill=(17, 24, 39, 255))
    return image