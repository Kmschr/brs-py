import uuid
import zlib
from .utils import ue4_basetime

class Writer:
    def __init__(self, buffer):
        self.buffer = buffer

    def write(self, barr):
        self.buffer.write(barr)

    def write_compressed(self, barr, should_compress=True):
        if not should_compress:
            self.u32(len(barr))
            self.u32(0)
            self.write(barr)
            return
        
        compressed = zlib.compress(barr)
        uncompressed_len = len(barr)
        compressed_len = len(compressed)
        self.u32(uncompressed_len)
        if uncompressed_len <= compressed_len:
            self.u32(0)
            self.write(barr)
        else:
            self.u32(compressed_len)
            self.write(compressed)

    def u8(self, val):
        self.buffer.write(val.to_bytes(1, "little"))

    def u16(self, val):
        self.buffer.write(val.to_bytes(2, "little"))

    def u32(self, val):
        self.buffer.write(val.to_bytes(4, "little"))

    def u64(self, val):
        self.buffer.write(val.to_bytes(8, "little"))

    def u32_bits(self, val):
        self.bitss(val.to_bytes(4, "little"), 32)

    def int_max(self, val, max_val):
        new_val = 0
        mask = 1
        while new_val + mask < max_val:
            self.buffer.write_bit(val & mask != 0)
            if val & mask != 0:
                new_val |= mask
            mask = mask << 1

    def int_packed(self, val):
        while True:
            src = val & 0x7F
            val = val >> 7
            self.bit(val != 0)
            self.bits(src, 7)
            if val == 0:
                break

    def id(self, id):
        a = bytearray(id.bytes[0:4])
        b = bytearray(id.bytes[4:8])
        c = bytearray(id.bytes[8:12])
        d = bytearray(id.bytes[12:16])
        a.reverse()
        b.reverse()
        c.reverse()
        d.reverse()
        self.buffer.write(a+b+c+d)

    def datetime(self, time):
        delta = time - ue4_basetime()
        seconds = int(delta.total_seconds())
        self.u64(seconds * 10000000)

    def user_name_first(self, user):
        self.string(user.name)
        self.id(user.uuid)

    def brick_owner(self, owner):
        self.id(owner.uuid)
        self.string(owner.name)
        self.u32(owner.brickcount)

    def string(self, val):
        self.u32(len(val)+1)
        self.write(val.encode('utf-8'))
        self.write(b'\0')

    def color(self, col):
        self.u32(col.val)

    def array(self, arrlen, func):
        self.u32(arrlen)
        for i in range(arrlen):
            func(i)

    def flush_byte(self):
        self.buffer.flush_byte()

    def bit(self, val):
        self.buffer.write_bit(val)

    def bits(self, val, size):
        for i in range(size):
            self.bit(val & (1 << (i & 7)) != 0)

    def bitss(self, val, size):
        for i in range(size):
            self.bit((val[i >> 3] & 0xFF) & (1 << (i & 7)) != 0)

    def positive_int_vector_packed(self, vec):
        self.int_packed(vec[0])
        self.int_packed(vec[1])
        self.int_packed(vec[2])

    def int_vector_packed(self, vec):
        f = lambda x : (abs(x) << 1) | (1 if x > 0 else 0)
        self.int_packed(f(vec[0]))
        self.int_packed(f(vec[1]))
        self.int_packed(f(vec[2]))