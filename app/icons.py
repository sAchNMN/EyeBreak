from __future__ import annotations

import sys
import tkinter as tk
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageTk

from app.paths import runtime_file_path


ICON_PATH = runtime_file_path("assets/eyebreak.ico")
APP_USER_MODEL_ID = "EyeBreak.Desktop.Reminder"


def ensure_icon_file(path: Path = ICON_PATH) -> Path:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            create_icon_image(256).save(
                path,
                format="ICO",
                sizes=[
                    (16, 16),
                    (24, 24),
                    (32, 32),
                    (48, 48),
                    (64, 64),
                    (128, 128),
                    (256, 256),
                ],
            )
    except OSError:
        return path
    return path


def create_icon_image(size: int = 64) -> Image.Image:
    image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    radius = round(size * 0.22)
    draw.rounded_rectangle(
        (0, 0, size - 1, size - 1),
        radius=radius,
        fill=(15, 23, 42, 255),
    )

    glow = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.ellipse(
        (size * 0.08, size * 0.04, size * 0.92, size * 0.88),
        fill=(45, 212, 191, 80),
    )
    image.alpha_composite(glow.filter(ImageFilter.GaussianBlur(size * 0.08)))

    draw = ImageDraw.Draw(image)
    eye_box = (
        round(size * 0.15),
        round(size * 0.26),
        round(size * 0.85),
        round(size * 0.68),
    )
    draw.ellipse(eye_box, fill=(241, 245, 249, 255))

    iris_box = (
        round(size * 0.35),
        round(size * 0.31),
        round(size * 0.65),
        round(size * 0.61),
    )
    draw.ellipse(iris_box, fill=(20, 184, 166, 255))

    pupil_box = (
        round(size * 0.44),
        round(size * 0.40),
        round(size * 0.56),
        round(size * 0.52),
    )
    draw.ellipse(pupil_box, fill=(15, 23, 42, 255))

    highlight_box = (
        round(size * 0.39),
        round(size * 0.34),
        round(size * 0.47),
        round(size * 0.42),
    )
    draw.ellipse(highlight_box, fill=(255, 255, 255, 230))

    horizon_y = round(size * 0.78)
    draw.line(
        (round(size * 0.22), horizon_y, round(size * 0.78), horizon_y),
        fill=(45, 212, 191, 255),
        width=max(2, round(size * 0.04)),
    )
    draw.arc(
        (
            round(size * 0.32),
            round(size * 0.62),
            round(size * 0.68),
            round(size * 0.94),
        ),
        start=200,
        end=340,
        fill=(45, 212, 191, 230),
        width=max(1, round(size * 0.025)),
    )

    return image


def apply_window_icon(window: tk.Tk | tk.Toplevel) -> None:
    icon_path = ensure_icon_file().resolve()
    try:
        window.iconbitmap(default=str(icon_path))
    except tk.TclError:
        pass

    try:
        photo = ImageTk.PhotoImage(create_icon_image(256))
        window.iconphoto(True, photo)
        window._eyebreak_icon_photo = photo
    except tk.TclError:
        pass


def set_windows_app_user_model_id(app_id: str = APP_USER_MODEL_ID) -> None:
    if sys.platform != "win32":
        return

    try:
        import ctypes

        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
    except (AttributeError, OSError, ValueError):
        return
