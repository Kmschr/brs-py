import pytest
from brs.brs import Brick

def test_brick_from_bounds():
    """Test creating a brick from bounds."""
    min_pos = [0, 0, 0]
    max_pos = [10, 10, 10]
    
    brick = Brick.from_bounds(min_pos, max_pos)
    
    assert brick.position == [5, 5, 5]
    assert brick.size == [5, 5, 5]

def test_brick_get_bounds():
    """Test getting bounds from a brick."""
    brick = Brick()
    brick.position = [5, 5, 5]
    brick.size = [5, 5, 5]
    
    min_pos, max_pos = brick.get_bounds()
    
    assert min_pos == [0, 0, 0]
    assert max_pos == [10, 10, 10]

def test_brick_bounds_roundtrip():
    """Test roundtrip from bounds to brick and back."""
    original_min = [10, 20, 30]
    original_max = [20, 40, 60]
    
    brick = Brick.from_bounds(original_min, original_max)
    min_pos, max_pos = brick.get_bounds()
    
    assert min_pos == original_min
    assert max_pos == original_max

def test_brick_from_bounds_negative():
    """Test creating a brick from bounds with negative coordinates."""
    min_pos = [-10, -10, -10]
    max_pos = [0, 0, 0]
    
    brick = Brick.from_bounds(min_pos, max_pos)
    
    assert brick.position == [-5, -5, -5]
    assert brick.size == [5, 5, 5]
