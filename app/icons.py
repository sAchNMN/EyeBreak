from __future__ import annotations

import math
import sys
import tkinter as tk
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageTk

from app.paths import runtime_file_path


ICON_PATH = runtime_file_path("assets/eyebreak.ico")
APP_USER_MODEL_ID = "EyeBreak.Desktop.Reminder"
ICON_SIZES = (16, 20, 24, 32, 40, 48, 64, 128, 256)

_RESAMPLING = getattr(Image, "Resampling", Image)


def ensure_icon_file(path: Path = ICON_PATH) -> Path:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            _write_icon_file(path)
    except OSError:
        return path
    return path


def _write_icon_file(path: Path) -> None:
    master = create_icon_image(256)
    extras = [create_icon_image(size) for size in ICON_SIZES if size != 256]
    master.save(
        path,
        format="ICO",
        sizes=[(size, size) for size in ICON_SIZES],
        append_images=extras,
    )


def create_icon_image(size: int = 64) -> Image.Image:
    """Return a fresh RGBA icon image at the requested square size."""
    return _render_icon_cached(int(size)).copy()


@lru_cache(maxsize=16)
def _render_icon_cached(size: int) -> Image.Image:
    return _render_icon(size)


def _render_icon(size: int) -> Image.Image:
    scale = 4 if size <= 64 else 2
    canvas = size * scale
    rich = size >= 40
    flair = size >= 96

    image = _paint_tile(canvas, rich)
    cx, cy = canvas * 0.5, canvas * 0.505
    hw, hh = canvas * 0.320, canvas * 0.170
    eye = _eye_polygon(cx, cy, hw, hh)

    if rich:
        shadow = Image.new("RGBA", (canvas, canvas), (0, 0, 0, 0))
        ImageDraw.Draw(shadow).polygon(
            _eye_polygon(cx, cy + canvas * 0.026, hw, hh),
            fill=(0, 0, 0, 110),
        )
        image.alpha_composite(
            shadow.filter(ImageFilter.GaussianBlur(canvas * 0.018))
        )

    eye_mask = Image.new("L", (canvas, canvas), 0)
    ImageDraw.Draw(eye_mask).polygon(eye, fill=255)
    if rich:
        eye_fill = _linear_gradient(
            canvas,
            [(0.0, (255, 255, 255)), (0.55, (246, 255, 253)),
             (1.0, (204, 251, 241))],
            90,
        )
    else:
        eye_fill = Image.new("RGBA", (canvas, canvas), (243, 255, 252, 255))
    eye_image = Image.new("RGBA", (canvas, canvas), (0, 0, 0, 0))
    eye_image.paste(eye_fill, (0, 0), eye_mask)
    image.alpha_composite(eye_image)

    if rich:
        ImageDraw.Draw(image).line(
            eye + [eye[0]],
            fill=(255, 255, 255, 255),
            width=max(1, round(canvas * 0.0035)),
            joint="curve",
        )

    draw = ImageDraw.Draw(image)
    iris_outer = canvas * 0.122
    draw.ellipse(
        (cx - iris_outer, cy - iris_outer, cx + iris_outer, cy + iris_outer),
        fill=(5, 47, 45, 255),
    )

    iris_radius = canvas * 0.111
    iris = _linear_gradient(
        round(iris_radius * 2),
        [(0.0, (153, 246, 228)), (0.52, (45, 212, 191)),
         (1.0, (13, 148, 136))],
        55,
    )
    iris_mask = Image.new("L", iris.size, 0)
    ImageDraw.Draw(iris_mask).ellipse(
        (0, 0, iris.size[0] - 1, iris.size[1] - 1), fill=255
    )
    iris_layer = Image.new("RGBA", (canvas, canvas), (0, 0, 0, 0))
    iris_layer.paste(
        iris,
        (round(cx - iris_radius), round(cy - iris_radius)),
        iris_mask,
    )
    image.alpha_composite(iris_layer)

    pupil_radius = canvas * (0.068 if size < 40 else 0.050)
    draw.ellipse(
        (cx - pupil_radius, cy - pupil_radius,
         cx + pupil_radius, cy + pupil_radius),
        fill=(3, 26, 26, 255),
    )

    if size >= 32:
        radius = canvas * (0.024 if size >= 48 else 0.026)
        hx, hy = cx - canvas * 0.038, cy - canvas * 0.042
        draw.ellipse(
            (hx - radius, hy - radius, hx + radius, hy + radius),
            fill=(255, 255, 255, 255),
        )

    if flair:
        radius = canvas * 0.009
        draw.ellipse(
            (cx + canvas * 0.033 - radius, cy + canvas * 0.038 - radius,
             cx + canvas * 0.033 + radius, cy + canvas * 0.038 + radius),
            fill=(251, 191, 36, 255),
        )
        _four_point_star(
            draw, canvas * 0.792, canvas * 0.235, canvas * 0.047,
            (251, 191, 36, 255),
        )
        _four_point_star(
            draw, canvas * 0.862, canvas * 0.322, canvas * 0.017,
            (253, 230, 138, 255),
        )

    return image.resize((size, size), _RESAMPLING.BOX)


def _paint_tile(size: int, rich: bool) -> Image.Image:
    mask = _rounded_mask(size, round(size * 0.225))
    image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    image.paste(
        _linear_gradient(
            size,
            [(0.0, (4, 32, 31)), (0.40, (8, 64, 60)),
             (0.75, (13, 106, 100)), (1.0, (17, 140, 132))],
            42,
        ),
        (0, 0),
        mask,
    )

    if rich:
        glow = _radial_glow(size, (0.28, 0.16), 0.62, (94, 234, 212), 52)
        glow.alpha_composite(
            _radial_glow(size, (0.86, 0.90), 0.56, (45, 212, 191), 30)
        )
        glow.putalpha(ImageChops.multiply(glow.getchannel("A"), mask))
        image.alpha_composite(glow)

        gloss_mask = Image.new("L", (1, 256), 0)
        gloss_pixels = gloss_mask.load()
        for y in range(256):
            t = y / 256
            gloss_pixels[0, y] = round(max(0.0, 1.0 - t / 0.52) ** 2 * 24)
        gloss_mask = gloss_mask.resize((size, size), _RESAMPLING.BILINEAR)
        gloss_mask = ImageChops.multiply(gloss_mask, mask)
        gloss = Image.new("RGBA", (size, size), (255, 255, 255, 255))
        gloss.putalpha(gloss_mask)
        image.alpha_composite(gloss)

        inset = max(2, round(size * 0.008))
        rim = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        ImageDraw.Draw(rim).rounded_rectangle(
            (inset, inset, size - inset - 1, size - inset - 1),
            radius=round(size * 0.225) - inset,
            outline=(255, 255, 255, 36),
            width=max(2, round(size * 0.006)),
        )
        image.alpha_composite(rim)

    image.putalpha(ImageChops.multiply(image.getchannel("A"), mask))
    return image


def _linear_gradient(size: int, stops, angle_deg: float) -> Image.Image:
    sample = 160
    image = Image.new("RGBA", (sample, sample))
    pixels = image.load()
    radians = math.radians(angle_deg)
    dx, dy = math.cos(radians), math.sin(radians)
    corners = ((0, 0), (sample, sample))
    projected = [
        (x / sample - 0.5) * dx + (y / sample - 0.5) * dy
        for x, y in corners
    ]
    low, high = min(projected), max(projected)

    for y in range(sample):
        for x in range(sample):
            t = ((x / sample - 0.5) * dx + (y / sample - 0.5) * dy - low) / (
                high - low
            )
            t = max(0.0, min(1.0, t))
            for index in range(len(stops) - 1):
                start, start_color = stops[index]
                end, end_color = stops[index + 1]
                if start <= t <= end:
                    local = (t - start) / (end - start) if end > start else 0.0
                    pixels[x, y] = (
                        *_mix(start_color, end_color, local),
                        255,
                    )
                    break

    return image.resize((size, size), _RESAMPLING.LANCZOS)


def _radial_glow(
    size: int,
    center: tuple[float, float],
    radius: float,
    color: tuple[int, int, int],
    peak_alpha: int,
) -> Image.Image:
    sample = 96
    alpha = Image.new("L", (sample, sample), 0)
    pixels = alpha.load()
    cx, cy = center[0] * sample, center[1] * sample
    sample_radius = radius * sample
    for y in range(sample):
        for x in range(sample):
            distance = math.hypot(x - cx, y - cy) / sample_radius
            if distance < 1:
                pixels[x, y] = round((1 - distance) ** 2 * peak_alpha)
    layer = Image.new("RGBA", (size, size), (*color, 0))
    layer.putalpha(alpha.resize((size, size), _RESAMPLING.LANCZOS))
    return layer


def _rounded_mask(size: int, radius: int) -> Image.Image:
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        (0, 0, size - 1, size - 1), radius=radius, fill=255
    )
    return mask


def _eye_polygon(
    cx: float, cy: float, half_width: float, half_height: float
) -> list[tuple[float, float]]:
    top = _bezier(
        (cx - half_width, cy),
        (cx - half_width * 0.52, cy - half_height * 1.38),
        (cx + half_width * 0.52, cy - half_height * 1.38),
        (cx + half_width, cy),
    )
    bottom = _bezier(
        (cx + half_width, cy),
        (cx + half_width * 0.55, cy + half_height * 1.18),
        (cx - half_width * 0.55, cy + half_height * 1.18),
        (cx - half_width, cy),
    )
    return top + bottom[1:]


def _bezier(
    p0: tuple[float, float],
    p1: tuple[float, float],
    p2: tuple[float, float],
    p3: tuple[float, float],
    count: int = 180,
) -> list[tuple[float, float]]:
    points = []
    for index in range(count + 1):
        t = index / count
        mt = 1 - t
        points.append(
            (
                mt**3 * p0[0] + 3 * mt**2 * t * p1[0]
                + 3 * mt * t**2 * p2[0] + t**3 * p3[0],
                mt**3 * p0[1] + 3 * mt**2 * t * p1[1]
                + 3 * mt * t**2 * p2[1] + t**3 * p3[1],
            )
        )
    return points


def _four_point_star(
    draw: ImageDraw.ImageDraw,
    cx: float,
    cy: float,
    radius: float,
    color: tuple[int, int, int, int],
) -> None:
    points = []
    for index in range(8):
        angle = -math.pi / 2 + index * math.pi / 4
        r = radius if index % 2 == 0 else radius * 0.24
        points.append((cx + math.cos(angle) * r, cy + math.sin(angle) * r))
    draw.polygon(points, fill=color)


def _mix(
    start: tuple[int, ...], end: tuple[int, ...], t: float
) -> tuple[int, ...]:
    return tuple(round(start[i] + (end[i] - start[i]) * t) for i in range(len(start)))


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