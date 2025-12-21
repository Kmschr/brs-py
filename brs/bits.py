"""Bit-level buffer classes for reading and writing binary data.

This module provides classes for reading and writing data at both byte
and bit granularity, used for Brickadia save file serialization.
"""
from typing import Optional


class Bytes:
    """Byte-oriented buffer for reading and writing.
    
    Attributes:
        buf: The underlying byte buffer.
        pos: Current position in bits.
    """
    
    def __init__(self, buf: bytes) -> None:
        """Initialize a Bytes buffer.
        
        Args:
            buf: Initial byte buffer.
        """
        self.buf = buf
        self.pos = 0

    def read(self, size: int) -> bytes:
        """Read bytes from the buffer.
        
        Args:
            size: Number of bytes to read.
            
        Returns:
            Bytes read from the buffer.
        """
        val = self.buf[(self.pos >> 3):(self.pos >> 3) + size]
        self.pos += (size << 3)
        return val

    def write(self, barr: bytes) -> None:
        """Write bytes to the buffer.
        
        Args:
            barr: Bytes to write.
        """
        self.buf += barr

    def __str__(self) -> str:
        """Decode buffer as UTF-8 string."""
        return self.buf.decode('utf-8')


class BitBuffer(Bytes):
    """Bit-oriented buffer for reading and writing individual bits.
    
    Extends Bytes with bit-level read/write operations.
    
    Attributes:
        buf: The underlying byte buffer.
        pos: Current position in bits.
        cur: Current byte being written.
        bit: Current bit position within cur.
    """
    
    def __init__(self, buf: bytes) -> None:
        """Initialize a BitBuffer.
        
        Args:
            buf: Initial byte buffer.
        """
        super().__init__(buf)
        self.cur = 0
        self.bit = 0

    def read_bit(self) -> bool:
        """Read a single bit from the buffer.
        
        Returns:
            Boolean value of the bit.
        """
        bit = (self.buf[self.pos >> 3] & (1 << (self.pos & 7))) != 0
        self.pos += 1
        return bit

    def write_bit(self, val: bool) -> None:
        """Write a single bit to the buffer.
        
        Args:
            val: Boolean value to write.
        """
        self.cur |= (1 if val else 0) << self.bit
        self.bit += 1
        if self.bit >= 8:
            self.flush_byte()

    def byte_align(self) -> None:
        """Align the read position to the next byte boundary."""
        self.pos = (self.pos + 7) & (~0x07)

    def flush_byte(self) -> None:
        """Flush the current partial byte to the buffer."""
        if self.bit > 0:
            self.write(self.cur.to_bytes(1, byteorder="little", signed=False))
            self.cur = 0
            self.bit = 0