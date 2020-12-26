import brs
import time

def test_read_write_read():
    start = time.time_ns()
    save = brs.readBRS("example_saves/Lighthouse_Island.brs")
    end = time.time_ns()

    print("Took {}s to read".format((end-start)/1e9))

    start = time.time_ns()
    brs.writeBRS("example_saves/ant.brs", save)
    end = time.time_ns()
    print("Took {}s to write".format((end-start)/1e9))

    brs.readBRS("example_saves/ant.brs", verbose=True)

def test_write_new():
    test = brs.default()
    for i in range(len(test.colors)):
        brick = brs.Brick.default()
        brick.owner_index = 0
        brick.position = [i * 10, 0, 6]
        brick.color = brs.Color(test.colors[i])
        test.bricks.append(brick)

    brs.writeBRS("example_saves/test.brs", test)
    brs.readBRS("example_saves/test.brs", verbose=True)

def test_brick():
    brick = brs.Brick.default()
    brick.asset_index = 1
    brick.position = [25, 25, 6]
    brick.owner_index = 4
    w = brs.writer.Writer(brs.bits.BitBuffer(b''))
    brs.brs._write_brick(w, brick, brs.default())

    for byte in w.buffer.buf:
        binary_string = "{:08b}".format(byte)
        print(binary_string)

    r = brs.reader.Reader(w.buffer)
    save = brs.default()
    brs.brs._read_brick(r, save)

def test_u32_bits():
    w = brs.writer.Writer(brs.bits.BitBuffer(b''))
    obj = brs.Color(1)
    obj.val = 507321
    w.u32_bits(obj)
    r = brs.reader.Reader(w.buffer)
    print(r.u32_bits())

brs.readBRS("example_saves/Lighthouse_Island.brs", verbose=True)