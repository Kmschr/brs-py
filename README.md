# brs-py

A robust savefile reader/writer for the Brickadia game.

[Brickadia](https://www.brickadia.com) is a multiplayer brick building game.

This library supports version 8 savefiles (Brickadia Alpha 5+).

## Features

- **Full Read/Write Support**: specific support for all save file features including bricks, components, and metadata.
- **Type Safe**: Fully type-hinted codebase for better development experience.
- **Efficient**: Bit-level reading/writing optimization.
- **No External Dependencies**: Works with standard Python library (requests/etc not needed).

## Install

```bash
pip3 install brs-py
```

## Example Usage

### Display info about a save
```python
import brs

# Read a save file
save = brs.readBRS("Freebuild.brs")
print(save)
```

### Make a save from scratch
```python
import brs
from brs.color import Color

# Create a default save
save = brs.default()

# Add some bricks
for color_index in range(len(save.colors)):
    brick = brs.Brick.default()
    brick.position = [color_index * 10, 0, 6]
    brick.color = Color(save.colors[color_index])
    save.bricks.append(brick)

# Write to file
brs.writeBRS("colors.brs", save)
```

## Development

To set up for development:

```bash
pip install -e ".[dev]"
pytest
```

