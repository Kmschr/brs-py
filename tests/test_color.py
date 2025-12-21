import pytest
from brs.color import Color, ColorMode

def test_color_mode():
    cm = ColorMode(5)
    assert cm.val == 5
    assert str(cm) == "5"

def test_color_mode_validation():
    with pytest.raises(ValueError):
        ColorMode(-1)

def test_color_init():
    c = Color(0xFF0000FF)
    assert c.val == 0xFF0000FF
    
    c2 = Color(c)
    assert c2.val == c.val

def test_color_from_rgba():
    c = Color.from_rgba(255, 0, 0, 255) # Red
    assert c.to_rgba() == (255, 0, 0, 255)
    # BGRA: FF 00 00 FF -> FF 00 00 FF (little endian is different but value is constructed by shifts)
    # b << 24 | g << 16 | r << 8 | a
    # 0 << 24 | 0 << 16 | 255 << 8 | 255
    # 0 | 0 | 0xFF00 | 0xFF = 0xFFFF
    assert c.val == 0x0000FFFF 

def test_color_to_rgba():
    c = Color.from_rgba(10, 20, 30, 40)
    assert c.to_rgba() == (10, 20, 30, 40)

def test_color_str():
    c = Color.from_rgba(255, 0, 0, 255)
    assert str(c) == "#ff0000ff"

def test_color_validation():
    with pytest.raises(ValueError):
        Color.from_rgba(256, 0, 0, 0)
    with pytest.raises(ValueError):
        Color.from_rgba(0, -1, 0, 0)
