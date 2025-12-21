import pytest
from brs.color import Color, ColorMode, convert_srgb_channel

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

def test_convert_srgb_channel():
    # 0 map to 0
    assert convert_srgb_channel(0) == 0
    # 255 maps to 255
    assert convert_srgb_channel(255) == 255
    
    # Mid-range matches standard sRGB -> Linear conversion
    # 127 in sRGB is approx 0.21 in linear energy, mapped back to 0-255 range? 
    # NO, the function maps sRGB (gamma) -> Linear (approx) then scales to 255.
    # Actually wait, obj2brs logic seems to go sRGB -> "Brickadia Space".
    # Let's check a few sample points from the formula.
    # c = 127/255 = 0.498
    # val = ((0.498 / 1.055) + 0.0521...) ** 2.4
    # val ~= (0.472 + 0.052) ** 2.4 ~= 0.524 ** 2.4 ~= 0.21
    # 0.21 * 255 ~= 53
    # So 127 should become around 53 or 54.
    assert 50 <= convert_srgb_channel(127) <= 60

def test_color_from_srgb():
    # White stays white
    c = Color.from_srgb(255, 255, 255)
    assert c.to_rgba() == (255, 255, 255, 255)
    
    # Black stays black
    c = Color.from_srgb(0, 0, 0)
    assert c.to_rgba() == (0, 0, 0, 255)
    
    # Red 255 stays 255
    # Green 127 drops significantly
    c = Color.from_srgb(255, 127, 0)
    r, g, b, a = c.to_rgba()
    assert r == 255
    assert 50 <= g <= 60
    assert b == 0
    assert a == 255

def test_constants():
    assert Color.RED.to_rgba() == (255, 0, 0, 255)
    assert Color.BLUE.to_rgba() == (0, 0, 255, 255)
    assert Color.GREEN.to_rgba() == (0, 255, 0, 255)
