import pytest
from brs.bits import Bytes, BitBuffer

def test_bytes_read_write():
    b = Bytes(b'')
    b.write(b'hello')
    assert b.buf == b'hello'
    assert b.read(5) == b'hello'
    assert b.pos == 40  # 5 * 8

def test_bitbuffer_bit_ops():
    bb = BitBuffer(b'')
    # Write bits: 1, 0, 1
    bb.write_bit(True)
    bb.write_bit(False)
    bb.write_bit(True)
    bb.flush_byte()
    
    # 10100000 (LSB first packing? Let's check logic:
    # bit 0: 1 -> cur |= 1 << 0 -> 1
    # bit 1: 0 -> cur |= 0 << 1 -> 1
    # bit 2: 1 -> cur |= 1 << 2 -> 1 | 4 = 5
    # flush: 5 (0x05)
    
    assert bb.buf == b'\x05'
    
    # Read back
    bb.pos = 0
    assert bb.read_bit() is True
    assert bb.read_bit() is False
    assert bb.read_bit() is True
    assert bb.read_bit() is False # 0 initialized rest

def test_bitbuffer_byte_align():
    bb = BitBuffer(b'\xFF\xFF') # 11111111 11111111
    bb.read_bit() # pos = 1
    bb.byte_align() # pos should align to 8
    assert bb.pos == 8
    val = bb.read(1) # reads next byte
    assert val == b'\xFF'
