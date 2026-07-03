from app.tray import _create_icon_image


def test_create_icon_image_has_expected_shape() -> None:
    image = _create_icon_image()

    assert image.size == (64, 64)
    assert image.mode == "RGBA"