from datetime import datetime
from .orientation import Direction, Rotation

def ue4_basetime():
    return datetime(1, 1, 1, 0, 0, 0)

def read_orientation(orientation):
    direction = Direction((orientation >> 2) % 6)
    rotation = Rotation(orientation & 0b11)
    return (direction, rotation)

def pack_orientation(direction, rotation):
    return (direction.value << 2) | rotation.value