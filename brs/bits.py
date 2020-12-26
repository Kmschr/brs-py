class Bytes:
    def __init__(self, buf):
        self.buf = buf
        self.pos = 0

    def read(self, size):
        val = self.buf[(self.pos >> 3):(self.pos >> 3)+size]
        self.pos += (size << 3)
        return val

    def write(self, barr):
        self.buf += barr

    def __str__(self):
        return self.buf.decode('utf-8')

class BitBuffer(Bytes):
    def __init__(self, buf):
        super().__init__(buf)
        self.cur = 0
        self.bit = 0

    def read_bit(self):
        bit = (self.buf[self.pos >> 3] & (1 << (self.pos & 7))) != 0
        self.pos += 1
        return bit

    def write_bit(self, val):
        self.cur |= (1 if val else 0) << self.bit
        self.bit += 1
        if self.bit >= 8:
            self.flush_byte()

    def byte_align(self):
        self.pos = (self.pos + 7) & (~0x07)

    def flush_byte(self):
        if self.bit > 0:
            self.write(self.cur.to_bytes(1, byteorder="little", signed=False))
            self.cur = 0
            self.bit = 0