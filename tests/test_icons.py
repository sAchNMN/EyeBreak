from app.icons import create_icon_image, ensure_icon_file


def test_create_icon_image_returns_rgba_square() -> None:
    image = create_icon_image(64)

    assert image.size == (64, 64)
    assert image.mode == "RGBA"


def test_ensure_icon_file_creates_ico(tmp_path) -> None:
    icon_path = tmp_path / "eyebreak.ico"

    result = ensure_icon_file(icon_path)

    assert result == icon_path
    assert icon_path.exists()
    assert icon_path.stat().st_size > 0