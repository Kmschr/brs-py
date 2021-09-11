import zlib
import uuid
import datetime
import textwrap
from enum import Enum
from .reader import Reader
from .writer import Writer
from .user import User
from .utils import read_orientation, pack_orientation
from .color import *
from .bits import *
from .orientation import *

_MAGIC = b'BRS'
_VERSION = 8
_GAME_VERSION = 6094

class ScreenshotFormat(Enum):
    NONE = 0
    PNG = 1

class Component():
    def __init__(self):
        self.version = None
        self.brick_indices = None
        self.properties = []

class Brick():
    def __init__(self):
        self.asset_index = None
        self.size = None
        self.position = None
        self.color = None
        self.direction = None
        self.rotation = None
        self.collision = None
        self.visibility = None
        self.material_index = None
        self.owner_index = None
        self.components = None

    @staticmethod
    def default():
        brick = Brick()
        brick.asset_index = 0
        brick.size = [5, 5, 6]
        brick.position = [0, 0, 6]
        brick.color = ColorMode(0)
        brick.direction = Direction.ZPositive
        brick.rotation = Rotation.Deg0
        brick.collision = True
        brick.visibility = True
        brick.material_index = 2
        brick.owner_index = 0
        return brick

    def __str__(self):
        return '''\
            Asset Index: {}
            Size: {}
            Position: {}
            Color: {}
            Direction: {}
            Rotation: {}
            Collision: {}
            Visibility: {}
            Material Index: {}
            Owner Index: {}
            '''.format(self.asset_index, self.size, self.position, self.color, self.direction, self.rotation, self.collision, self.visibility, self.material_index, self.owner_index)

class BRS:
    def __init__(self):
        self.version = None
        self.game_version = None
        self.map = None
        self.description = None
        self.author = None
        self.host = None
        self.time = None
        self.brickcount = None
        self.mods = []
        self.brick_assets = []
        self.colors = []
        self.materials = []
        self.brick_owners = []
        self.screenshot_data = None
        self.bricks = []
        self.components = dict()

    def __str__(self):
        return textwrap.dedent('''\
        Version {}
        Game Version {}
        Map: {}
        Description: {}
        Author: {}
        Host: {}
        Savetime: {}
        Brickcount: {}
        Mods: {}
        Brick Assets: {}
        Colors: {}
        Materials: {}
        Brick Owners: {}'''.format(self.version, self.game_version, self.map, self.description, self.author, self.host, self.time, len(self.bricks), self.mods, self.brick_assets, self.colors, self.materials, self.brick_owners))

def readBRS(filename, verbose=False):
    # Read Preamble
    if verbose:
        print("Reading", filename)
    brs = open(filename, "rb")
    r = Reader(brs)
    magic = r.read(3)
    if magic != _MAGIC:
        raise Exception("Not a valid BRS file")
    save = BRS()
    save.version = r.u16()
    save.game_version = r.u32()

    # Read Header 1
    r.buffer = r.read_compressed()
    save.map = r.string()
    author_name = r.string()
    save.description = r.string()
    author_id = r.id()
    save.author = User(author_name, author_id)
    save.host = r.user_name_first()
    save.time = r.datetime()
    save.brickcount = r.u32()
    if verbose:
        print("Map:", save.map)
        print("Description:", save.description)
        print("Author:", save.author) 
        print("Host:", save.host)
        print("Savetime:", save.time)
        print("Brickcount: {:,}".format(save.brickcount))

    # Read Header 2
    r.buffer = brs
    r.buffer = r.read_compressed()
    save.mods = r.array(r.string)
    save.brick_assets = r.array(r.string)
    save.colors = r.array(r.color)
    save.materials = r.array(r.string)
    save.brick_owners = r.array(r.brick_owner)
    if verbose:
        print("Mods:", save.mods)
        print("Brick Assets:", save.brick_assets)
        print("Colors:", save.colors)
        print("Materials:", save.materials)
        print("Brick Owners:", save.brick_owners)

    # Read Screenshot
    r.buffer = brs
    screenshot_format = ScreenshotFormat(r.u8())
    if verbose:
        print("Screenshot Format:", screenshot_format.name)
    if screenshot_format == ScreenshotFormat.PNG:
        screenshot_data_len = r.u32()
        save.screenshot_data = r.read(screenshot_data_len)

    # Read bricks
    r.buffer = r.read_compressed()
    save.bricks = []
    for _ in range(save.brickcount):
        _read_brick(r, save)

    if verbose:
        print("Bricks:", len(save.bricks))

    # Read components
    r.buffer = brs
    r.buffer = r.read_compressed()
    num_components = r.u32()
    for _ in range(num_components):
        name = r.string()
        r.u32()
        version = r.u32()
        if verbose:
            print("{} (v{})".format(name, version))
        indices = r.array_bits(lambda: r.int_max(max(len(save.bricks), 2)))
        if verbose:
            print("Bricks:", len(indices))
        properties = r.array_bits(lambda: [r.string_bits(), r.string_bits()])
        if verbose:
            print("Properties:",properties)
        for i in indices:
            props = dict()
            for prop in properties:
                props[prop[0]] = r.unreal(prop[1])
            if save.bricks[i].components is None:
                save.bricks[i].components = dict()
            save.bricks[i].components[name] = props
        component = Component()
        component.version = version
        component.brick_indices = indices
        component.properties = properties
        save.components[name] = component
        r.byte_align()
    brs.close()
    return save

def _read_brick(r, save):
    brick = Brick()
    brick.asset_index = r.int_max(max(len(save.brick_assets), 2))
    brick.size = [0, 0, 0]
    if r.read_bit():
        brick.size = r.positive_int_vector_packed()
    brick.position = r.int_vector_packed()
    orientation = r.int_max(24)
    dirrot = read_orientation(orientation)
    brick.direction = dirrot[0]
    brick.rotation = dirrot[1]
    brick.collision = r.read_bit()
    brick.visibility = r.read_bit()
    brick.material_index = r.int_max(max(len(save.materials), 2))
    if not r.read_bit():
        brick.color = ColorMode(r.int_max(len(save.colors)))
    else:
        brick.color = Color(r.u32_bits())
    brick.owner_index = r.int_packed()
    save.bricks.append(brick)
    r.byte_align()

def writeBRS(filename, save, compressed=True):
    # Write Preamble
    brs = open(filename, "wb")
    w = Writer(brs)
    w.write(_MAGIC)
    w.u16(save.version)
    w.u32(save.game_version)

    # Write Header1
    h1 = Writer(Bytes(b''))
    h1.string(save.map)
    h1.string(save.author.name)
    h1.string(save.description)
    h1.id(save.author.uuid)
    h1.user_name_first(save.host)
    h1.datetime(save.time)
    h1.u32(len(save.bricks))
    w.write_compressed(h1.buffer.buf, compressed)

    # Write Header2
    h2 = Writer(Bytes(b''))
    h2.array(len(save.mods), lambda i : h2.string(save.mods[i]))
    h2.array(len(save.brick_assets), lambda i : h2.string(save.brick_assets[i]))
    h2.array(len(save.colors), lambda i : h2.color(save.colors[i]))
    h2.array(len(save.materials), lambda i : h2.string(save.materials[i]))
    h2.array(len(save.brick_owners), lambda i : h2.brick_owner(save.brick_owners[i]))
    w.write_compressed(h2.buffer.buf, compressed)

    # Write Screenshot
    if save.screenshot_data is not None:
        w.u8(ScreenshotFormat.PNG.value)
        w.u32(len(save.screenshot_data))
        w.write(save.screenshot_data)
    else:
        w.u8(ScreenshotFormat.NONE.value)

    # Write Bricks
    bricks = Writer(BitBuffer(b''))
    for brick in save.bricks:
        _write_brick(bricks, brick, save)
    w.write_compressed(bricks.buffer.buf, compressed)

def _write_brick(w, brick, save):
    w.int_max(brick.asset_index, max(len(save.brick_assets), 2))
    if all(v == 0 for v in brick.size):
        w.bit(False)
    else:
        w.bit(True)
        w.positive_int_vector_packed(brick.size)
    w.int_vector_packed(brick.position)
    w.int_max(pack_orientation(brick.direction, brick.rotation), 24)
    w.bit(brick.collision)
    w.bit(brick.visibility)
    w.int_max(brick.material_index, max(len(save.materials), 2))
    if isinstance(brick.color, Color):
        w.bit(True)
        w.u32_bits(brick.color.val)
    elif isinstance(brick.color, ColorMode):
        w.bit(False)
        w.int_max(brick.color.val, max(len(save.colors), 2))
    w.int_packed(brick.owner_index)
    w.flush_byte()

def default():
    save = BRS()
    save.version = _VERSION
    save.game_version = _GAME_VERSION
    save.map = 'Plate'
    save.description = 'made with brs-py'
    save.author = User('Smallguy', uuid.UUID('{8efaeb23-5e82-428e-b575-0dd30270146e}'))
    save.host = save.author
    save.brick_assets = ['PB_DefaultBrick']
    save.materials = ['BMC_Ghost', 'BMC_Ghost_Fail', 'BMC_Plastic', 'BMC_Glow', 'BMC_Metallic', 'BMC_Hologram']
    save.colors = [4294967295, 4287137928, 4284045657, 4281940281, 4280492835, 4279308561, 4278584838, 4278190080, 4283893001, 4293527046, 4294330630, 4293565702, 4278749701, 4278491306, 4288881493, 4284092983, 4279632897, 4281406477, 4284026884, 4287642642, 4289095742, 4294942542, 4290945850, 4294946607, 4278522373, 4278525442, 4279575552, 4278209536, 4278924810, 4282601228, 4294939146, 4285349893, 4278853163, 4280166185, 4282866784, 4286819509, 4283470754, 4278744776, 4278206586, 4278264384, 2583629326, 2583677957, 2568982546, 2569766333, 2572616969, 2583054598, 2567449359, 2583691263, 2583691263, 2575861896, 2572769625, 2570664249, 2569216803, 2568032529, 2567308806, 2566914048]
    for i in range(len(save.colors)):
        save.colors[i] = Color(save.colors[i])
    save.time = datetime.datetime.utcnow()
    return save
