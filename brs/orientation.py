"""Orientation enums for Brickadia bricks.

This module defines the direction and rotation enums used to specify
brick orientation in 3D space.
"""
from enum import Enum


class Rotation(Enum):
    """Brick rotation around its direction axis."""
    Deg0 = 0
    Deg90 = 1
    Deg180 = 2
    Deg270 = 3


class Direction(Enum):
    """Brick facing direction in 3D space."""
    XPositive = 0
    XNegative = 1
    YPositive = 2
    YNegative = 3
    ZPositive = 4
    ZNegative = 5
