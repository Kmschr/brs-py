"""Utility functions for Brickadia save file handling.

This module provides helper functions for datetime conversion and
brick orientation packing/unpacking.
"""
from datetime import datetime, timezone
from typing import Tuple
from .orientation import Direction, Rotation


def ue4_basetime() -> datetime:
    """Get the Unreal Engine 4 base time (January 1, 0001).
    
    Returns:
        datetime: The UE4 epoch datetime (UTC).
    """
    return datetime(1, 1, 1, 0, 0, 0, tzinfo=timezone.utc)


def read_orientation(orientation: int) -> Tuple[Direction, Rotation]:
    """Unpack orientation value into direction and rotation.
    
    Args:
        orientation: Packed orientation value (0-23).
        
    Returns:
        Tuple of (Direction, Rotation).
        
    Raises:
        ValueError: If orientation is out of valid range.
    """
    if not 0 <= orientation < 24:
        raise ValueError(f"Invalid orientation value: {orientation}. Must be 0-23.")
    direction = Direction((orientation >> 2) % 6)
    rotation = Rotation(orientation & 0b11)
    return (direction, rotation)


def pack_orientation(direction: Direction, rotation: Rotation) -> int:
    """Pack direction and rotation into a single orientation value.
    
    Args:
        direction: Brick facing direction.
        rotation: Brick rotation.
        
    Returns:
        Packed orientation value (0-23).
    """
    return (direction.value << 2) | rotation.value