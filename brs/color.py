"""Color classes for Brickadia bricks.

This module provides color representation for bricks, supporting both
indexed colors (ColorMode) and custom RGBA colors (Color).
"""
from typing import Tuple, Union


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
        """Create a Color from RGBA components.
        
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