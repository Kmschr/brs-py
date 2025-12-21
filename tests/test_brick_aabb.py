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

def test_brick_overlaps():
    """Test brick overlap AABB check."""
    # Base brick at [0,0,0] to [10,10,10]
    b1 = Brick.from_bounds([0, 0, 0], [10, 10, 10])
    
    # Overlapping (fully inside)
    b2 = Brick.from_bounds([2, 2, 2], [8, 8, 8])
    assert b1.overlaps(b2)
    assert b2.overlaps(b1)
    
    # Overlapping (partial)
    b3 = Brick.from_bounds([5, 5, 5], [15, 15, 15])
    assert b1.overlaps(b3)
    
    # Disjoint
    b4 = Brick.from_bounds([20, 0, 0], [30, 10, 10])
    assert not b1.overlaps(b4)
    
    # Touching faces (should NOT overlap)
    # b1 ends at 10. b5 starts at 10.
    b5 = Brick.from_bounds([10, 0, 0], [20, 10, 10])
    assert not b1.overlaps(b5)
    
    # Touching edge
    b6 = Brick.from_bounds([10, 10, 0], [20, 20, 10])
    assert not b1.overlaps(b6)
    
    # Touching corner
    b7 = Brick.from_bounds([10, 10, 10], [20, 20, 20])
    assert not b1.overlaps(b7)
