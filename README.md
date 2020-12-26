# brs-py

A savefile reader/writer for the Brickadia game

[Brickadia](https://www.brickadia.com) is a multiplayer brick building game

Made for version 8 savefiles (Brickadia Alpha 5)

## Install

```
pip3 install brs-py
```

## Example Usage

### Display info about a save
```python
import brs

save = brs.readBRS("Freebuild.brs")
print(save)
```

### Make a save from scratch, with bricks showing the default colorset
```python
import brs

save = brs.default()

for color_index in range(len(save.colors)):
    brick = brs.Brick.default()
    brick.position = [color_index * 10, 0, 6]
    brick.color = brs.ColorMode(save.colors[color_index])
    save.bricks.append(brick)

brs.writeBRS("colors.brs", save)
```