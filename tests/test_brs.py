import pytest
import os
import uuid
from brs.brs import default, writeBRS, readBRS, BRS, Brick
from brs.color import Color

def test_default_save():
    save = default()
    assert save.version == 8
    assert save.game_version == 6094
    assert len(save.bricks) == 0
    assert len(save.colors) > 0
    assert len(save.brick_assets) > 0
    assert len(save.materials) > 0
    assert len(save.brick_owners) == 1

def test_write_read_roundtrip(tmp_path):
    # Create a save
    save = default()
    
    # Add some bricks
    b1 = Brick.default()
    b1.position = [0, 0, 10]
    b1.color = Color(0xFF0000FF)
    save.bricks.append(b1)
    
    b2 = Brick.default()
    b2.position = [10, 10, 10]
    b2.asset_index = 0
    save.bricks.append(b2)
    
    save.brickcount = len(save.bricks)
    
    # Write
    path = tmp_path / "test.brs"
    writeBRS(str(path), save)
    
    # Read
    read_save = readBRS(str(path))
    
    assert read_save.version == save.version
    assert len(read_save.bricks) == len(save.bricks)
    assert read_save.bricks[0].position == b1.position
    # Note: Colors might need exact check depending on storage (Color vs ColorMode)
    # The default writer logic checks instance type.
    
    assert read_save.map == save.map
    assert read_save.author.name == save.author.name

def test_read_invalid_file(tmp_path):
    path = tmp_path / "invalid.brs"
    with open(path, "wb") as f:
        f.write(b"NOTBRS")
        
    with pytest.raises(Exception, match="Not a valid BRS file"):
        readBRS(str(path))
