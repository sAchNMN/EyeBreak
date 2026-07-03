from __future__ import annotations

from collections.abc import Callable

import pystray
from PIL import Image, ImageDraw


class TrayIcon:
    def __init__(
        self,
        on_break_now: Callable[[], None],
        on_pause: Callable[[], None],
        on_resume: Callable[[], None],
        on_exit: Callable[[], None],
    ) -> None:
        self.icon = pystray.Icon(
            "EyeBreak",
            _create_icon_image(),
            "EyeBreak",
            pystray.Menu(
                pystray.MenuItem("立即休息", lambda icon, item: on_break_now()),
                pystray.MenuItem("暂停", lambda icon, item: on_pause()),
                pystray.MenuItem("恢复", lambda icon, item: on_resume()),
                pystray.MenuItem("退出", lambda icon, item: on_exit()),
            ),
        )

    def start(self) -> None:
        self.icon.run_detached()

    def stop(self) -> None:
        self.icon.stop()


def _create_icon_image() -> Image.Image:
    image = Image.new("RGBA", (64, 64), (17, 24, 39, 255))
    draw = ImageDraw.Draw(image)
    draw.ellipse((10, 18, 54, 46), fill=(249, 250, 251, 255))
    draw.ellipse((23, 22, 41, 40), fill=(34, 197, 94, 255))
    draw.ellipse((29, 28, 35, 34), fill=(17, 24, 39, 255))
    return image