import uuid
import struct
import zlib
from datetime import timedelta
from .user import User, BrickOwner
from .utils import ue4_basetime
from .color import Color
from .bits import BitBuffer

class Reader:
    def __init__(self, buffer):
        self.buffer = buffer

    def read(self, size):
        return self.buffer.read(size)

    def read_bit(self):
        return self.buffer.read_bit()

    def byte_align(self):
        self.buffer.byte_align()

    def read_compressed(self):
        uncompressed_len = self.u32()
        compressed_len = self.u32()
        if compressed_len != 0:
            return BitBuffer(zlib.decompress(self.read(compressed_len), bufsize=uncompressed_len))
        else:
            return BitBuffer(self.buffer.read(uncompressed_len))

    def u8(self):
        return int.from_bytes(self.buffer.read(1), byteorder="little", signed=False)

    def u16(self):
        return int.from_bytes(self.buffer.read(2), byteorder="little", signed=False)

    def u32(self):
        return int.from_bytes(self.buffer.read(4), byteorder="little", signed=False)

    def i32(self):
        return int.from_bytes(self.buffer.read(4), byteorder="little", signed=True)

    def u64(self):
        return int.from_bytes(self.buffer.read(8), byteorder="little", signed=False)

    def u32_bits(self):
        arr = self.bits(32)
        return arr[3] << 24 | arr[2] << 16 | arr[1] << 8 | arr[0]

    def bits(self, size):
        dst = [0 for v in range(int(size/8))]
        for bit in range(size):
            shift = bit & 0x7
            dst[bit >> 3] = (dst[bit >> 3] & ~(1 << shift)) | ((1 if self.read_bit() else 0) << shift)
        return dst

    def int_max(self, max_val):
        val = 0
        mask = 1
        while val + mask < max_val:
            if self.buffer.read_bit():
                val |= mask
            mask = mask << 1
        return val

    def ascii(self, size):
        ascii_str = self.buffer.read(size-1).decode('utf-8')
        self.buffer.read(1)
        return ascii_str

    def ucs2(self, size):
        size = -size
        if size % 2 != 0:
            raise Exception("Invalid UCS-2 Size")
        ucs2_str = self.buffer.read(size-2).decode('utf-16')
        self.buffer.read(2)
        return ucs2_str

    def string(self):
        strlen = self.i32()
        if strlen >= 0:
            return self.ascii(strlen)
        else:
            return self.ucs2(strlen)

    def id(self):
        bytes_be = b''
        for _ in range(4):
            be = bytearray(self.buffer.read(4))
            be.reverse()
            bytes_be += be

        return uuid.UUID(bytes=bytes_be)

    def user_name_first(self):
        name = self.string()
        id = self.id()
        return User(name, id)

    def brick_owner(self):
        id = self.id()
        name = self.string()
        brickcount = self.u32()
        return BrickOwner(name, id, brickcount)

    def datetime(self):
        ticks = self.u64()
        micro = ticks / 10
        nano = (ticks % 10) * 100
        return ue4_basetime() + timedelta(microseconds=micro) + timedelta(microseconds=nano/1000)

    def color(self):
        return Color(self.u32())

    def array(self, func):
        size = self.u32()
        vals = []
        for _ in range(size):
            vals.append(func())
        return vals

    def array_bits(self, func):
        size = self.u32_bits()
        vals = []
        for _ in range(size):
            vals.append(func())
        return vals

    def int_packed(self):
        val = 0
        for i in range(5):
            has_next = self.buffer.read_bit()
            part = 0
            for bitshift in range(7):
                part |= (1 if self.buffer.read_bit() else 0) << bitshift
            val |= part << (7*i)
            if not has_next:
                break
        return val

    def positive_int_vector_packed(self):
        return [self.int_packed(), self.int_packed(), self.int_packed()]

    def signed_int_packed(self):
        val = self.int_packed()
        return (val >> 1) * 1 if ((val & 1) != 0) else -1

    def int_vector_packed(self):
        return [self.signed_int_packed(), self.signed_int_packed(), self.signed_int_packed()]

    def string_bits(self):
        size = self.u32_bits()
        stuff = self.bits(size * 8 - 8)
        self.bits(8)
        return ''.join([chr(c) for c in stuff])

    def float_bits(self):
        bits = self.bits(32)
        arr = b''
        for bit in bits:
            arr += bit.to_bytes(1, 'little')
        return struct.unpack('f', arr)[0]

    def unreal(self, val_type):
        if val_type == 'Class':
            return self.string_bits()
        elif val_type == 'Object':
            return self.string_bits()
        elif val_type == 'Boolean':
            return self.u32_bits() != 0
        elif val_type == 'Float':
            return self.float_bits()
        elif val_type == 'Color':
            return Color(self.u32_bits())
        elif val_type == 'Byte':
            return self.bits(8)[0].to_bytes(1, 'little')
        elif val_type == 'Rotator':
            return [self.float_bits(), self.float_bits(), self.float_bits()]
