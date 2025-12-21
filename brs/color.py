"""Color classes for Brickadia bricks.

This module provides color representation for bricks, supporting both
indexed colors (ColorMode) and custom RGBA colors (Color).
"""
from typing import Tuple, Union


def convert_srgb_channel(channel: int) -> int:
    """Convert an sRGB color channel (0-255) to Brickadia linear space.
    
    Ported from obj2brs/src/color.rs.
    """
    c = channel / 255.0
    if c > 0.04045:
        val = ((c / 1.055) + 0.052_132_7) ** 2.4
    else:
        val = c / 12.92
    
    return max(0, min(255, int(round(val * 255.0))))


class ColorMode:
    """Indexed color reference to the save file's color palette.
    
    Attributes:
        val: Index into the save file's color array.
    """
    
    def __init__(self, index: int) -> None:
        """Initialize a ColorMode with a palette index.
        
        Args:
            index: Index into the color palette.
            
        Raises:
            ValueError: If index is negative.
        """
        if index < 0:
            raise ValueError(f"Color index must be non-negative, got {index}")
        self.val = index

    def __str__(self) -> str:
        return str(self.val)


class Color(ColorMode):
    """Custom RGBA color for bricks.
    
    Colors are stored as 32-bit integers in BGRA byte order.
    
    Attributes:
        val: 32-bit BGRA color value.
    """
    
    def __init__(self, val: Union[int, 'Color']) -> None:
        """Initialize a Color from an integer or another Color.
        
        Args:
            val: Either a 32-bit BGRA integer or another Color instance.
        """
        if isinstance(val, Color):
            val = val.val
        super().__init__(val)

    @staticmethod
    def from_rgba(r: int, g: int, b: int, a: int) -> 'Color':
        """Create a Color from raw RGBA components.
        
        Args:
            r: Red component (0-255).
            g: Green component (0-255).
            b: Blue component (0-255).
            a: Alpha component (0-255).
            
        Returns:
            Color instance.
            
        Raises:
            ValueError: If any component is out of range.
        """
        for name, val in [('r', r), ('g', g), ('b', b), ('a', a)]:
            if not 0 <= val <= 255:
                raise ValueError(f"{name} must be 0-255, got {val}")
        return Color(b << 24 | g << 16 | r << 8 | a)

    @staticmethod
    def from_srgb(r: int, g: int, b: int, a: int = 255) -> 'Color':
        """Create a Color from sRGB components, applying gamma correction.
        
        Use this when converting colors from web hex codes or standard image files.
        Alpha is treated as linear and passed through unchanged.
        
        Args:
            r: Red component (0-255).
            g: Green component (0-255).
            b: Blue component (0-255).
            a: Alpha component (0-255, default 255).
        """
        return Color.from_rgba(
            convert_srgb_channel(r),
            convert_srgb_channel(g),
            convert_srgb_channel(b),
            a
        )
    
    def to_rgba(self) -> Tuple[int, int, int, int]:
        """Extract RGBA components from the color.
        
        Returns:
            Tuple of (r, g, b, a) values (0-255).
        """
        r = (self.val >> 8) & 0xFF
        g = (self.val >> 16) & 0xFF
        b = (self.val >> 24) & 0xFF
        a = self.val & 0xFF
        return (r, g, b, a)

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        """Format color as hex string (#RRGGBBAA)."""
        r, g, b, a = self.to_rgba()
        return '#{:02x}{:02x}{:02x}{:02x}'.format(r, g, b, a)

# Standard Colors (pre-converted from sRGB)

# Grayscale
Color.WHITE = Color.from_srgb(255, 255, 255)
Color.LIGHT_GRAY = Color.from_srgb(211, 211, 211)
Color.GRAY = Color.from_srgb(128, 128, 128)
Color.DARK_GRAY = Color.from_srgb(169, 169, 169)
Color.DARKER_GRAY = Color.from_srgb(64, 64, 64)
Color.BLACK = Color.from_srgb(0, 0, 0)

# Reds
Color.RED = Color.from_srgb(255, 0, 0)
Color.LIGHT_RED = Color.from_srgb(255, 102, 102)
Color.DARK_RED = Color.from_srgb(139, 0, 0)

# Oranges / Browns
Color.ORANGE = Color.from_srgb(255, 165, 0)
Color.LIGHT_ORANGE = Color.from_srgb(255, 204, 102)
Color.DARK_ORANGE = Color.from_srgb(255, 140, 0)
Color.BROWN = Color.from_srgb(165, 42, 42)
Color.LIGHT_BROWN = Color.from_srgb(210, 180, 140) # Tan
Color.DARK_BROWN = Color.from_srgb(101, 67, 33)

# Yellows
Color.YELLOW = Color.from_srgb(255, 255, 0)
Color.LIGHT_YELLOW = Color.from_srgb(255, 255, 153)
Color.GOLD = Color.from_srgb(255, 215, 0)

# Greens
Color.GREEN = Color.from_srgb(0, 255, 0) # Lime
Color.LIGHT_GREEN = Color.from_srgb(144, 238, 144)
Color.DARK_GREEN = Color.from_srgb(0, 100, 0)
Color.OLIVE = Color.from_srgb(128, 128, 0)

# Cyans / Teals
Color.CYAN = Color.from_srgb(0, 255, 255) # Aqua
Color.LIGHT_CYAN = Color.from_srgb(224, 255, 255)
Color.TEAL = Color.from_srgb(0, 128, 128)

# Blues
Color.BLUE = Color.from_srgb(0, 0, 255)
Color.LIGHT_BLUE = Color.from_srgb(173, 216, 230)
Color.SKY_BLUE = Color.from_srgb(135, 206, 235)
Color.DARK_BLUE = Color.from_srgb(0, 0, 139)
Color.NAVY = Color.from_srgb(0, 0, 128)

# Purples / Pinks
Color.MAGENTA = Color.from_srgb(255, 0, 255) # Fuchsia
Color.PURPLE = Color.from_srgb(128, 0, 128)
Color.VIOLET = Color.from_srgb(238, 130, 238)
Color.PINK = Color.from_srgb(255, 192, 203)
Color.LIGHT_PINK = Color.from_srgb(255, 182, 193)
Color.HOT_PINK = Color.from_srgb(255, 105, 180)