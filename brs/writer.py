"""Binary writer for Brickadia save files.

This module provides the Writer class for serializing Brickadia save files
to binary format, supporting both byte and bit-level operations.
"""
import uuid
import zlib
from datetime import datetime
from typing import Any, Callable, List, Union, Dict
from .utils import ue4_basetime
from .bits import Bytes, BitBuffer
from .user import User, BrickOwner
from .color import Color


class Writer:
    """Binary writer for serializing Brickadia save file data.
    
    Attributes:
        buffer: The underlying buffer to write to.
    """
    
    def __init__(self, buffer: Any) -> None:
        """Initialize a Writer with a buffer.
        
        Args:
            buffer: Buffer to write to (Bytes, BitBuffer, or file-like object).
        """
        self.buffer = buffer

    def write(self, barr: bytes) -> None:
        """Write raw bytes to the buffer.
        
        Args:
            barr: Bytes to write.
        """
        self.buffer.write(barr)

    def write_compressed(self, barr: bytes, should_compress: bool = True) -> None:
        """Write data with optional compression.
        
        Args:
            barr: Bytes to write.
            should_compress: Whether to compress the data.
        """
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

    def u8(self, val: int) -> None:
        """Write an unsigned 8-bit integer.
        
        Args:
            val: Value to write (0-255).
        """
        self.buffer.write(val.to_bytes(1, "little"))

    def u16(self, val: int) -> None:
        """Write an unsigned 16-bit integer.
        
        Args:
            val: Value to write.
        """
        self.buffer.write(val.to_bytes(2, "little"))

    def u32(self, val: int) -> None:
        """Write an unsigned 32-bit integer.
        
        Args:
            val: Value to write.
        """
        self.buffer.write(val.to_bytes(4, "little"))

    def u64(self, val: int) -> None:
        """Write an unsigned 64-bit integer.
        
        Args:
            val: Value to write.
        """
        self.buffer.write(val.to_bytes(8, "little"))

    def u32_bits(self, val: int) -> None:
        """Write a 32-bit unsigned integer to bit stream.
        
        Args:
            val: Value to write.
        """
        self.buffer.write_int(val, 32)

    def int_max(self, val: int, max_val: int) -> None:
        """Write a variable-length integer with a maximum value.
        
        Args:
            val: Value to write.
            max_val: Maximum possible value.
        """
        new_val = 0
        mask = 1
        while new_val + mask < max_val:
            self.buffer.write_bit(val & mask != 0)
            if val & mask != 0:
                new_val |= mask
            mask = mask << 1

    def int_packed(self, val: int) -> None:
        """Write a packed integer value.
        
        Args:
            val: Value to pack and write.
        """
        while True:
            src = val & 0x7F
            val = val >> 7
            self.bit(val != 0)
            self.bits(src, 7)
            if val == 0:
                break

    def id(self, id: uuid.UUID) -> None:
        """Write a UUID.
        
        Args:
            id: UUID to write.
        """
        a = bytearray(id.bytes[0:4])
        b = bytearray(id.bytes[4:8])
        c = bytearray(id.bytes[8:12])
        d = bytearray(id.bytes[12:16])
        a.reverse()
        b.reverse()
        c.reverse()
        d.reverse()
        self.buffer.write(a+b+c+d)

    def datetime(self, time: datetime) -> None:
        """Write a datetime value.
        
        Args:
            time: datetime to write.
        """
        delta = time - ue4_basetime()
        seconds = int(delta.total_seconds())
        self.u64(seconds * 10000000)

    def user_name_first(self, user: User) -> None:
        """Write a User with name before ID.
        
        Args:
            user: User to write.
        """
        self.string(user.name)
        self.id(user.uuid)

    def brick_owner(self, owner: BrickOwner) -> None:
        """Write a BrickOwner.
        
        Args:
            owner: BrickOwner to write.
        """
        self.id(owner.uuid)
        self.string(owner.name)
        self.u32(owner.brickcount)

    def string(self, val: str) -> None:
        """Write a string.
        
        Args:
            val: String to write.
        """
        self.u32(len(val)+1)
        self.write(val.encode('utf-8'))
        self.write(b'\0')

    def color(self, col: Color) -> None:
        """Write a Color value.
        
        Args:
            col: Color to write.
        """
        self.u32(col.val)

    def array(self, arrlen: int, func: Callable[[int], None]) -> None:
        """Write an array of values.
        
        Args:
            arrlen: Length of the array.
            func: Function to write each element, receives index as argument.
        """
        self.u32(arrlen)
        for i in range(arrlen):
            func(i)

    def flush_byte(self) -> None:
        """Flush the current partial byte to the buffer."""
        self.buffer.flush_byte()

    def bit(self, val: bool) -> None:
        """Write a single bit.
        
        Args:
            val: Boolean value to write.
        """
        self.buffer.write_bit(val)

    def bits(self, val: int, size: int) -> None:
        """Write multiple bits from an integer.
        
        Args:
            val: Integer containing bits to write.
            size: Number of bits to write.
        """
        self.buffer.write_int(val, size)

    def bitss(self, val: bytes, size: int) -> None:
        """Write multiple bits from a byte array.
        
        Args:
            val: Byte array containing bits to write.
            size: Number of bits to write.
        """
        for i in range(size):
            self.bit((val[i >> 3] & 0xFF) & (1 << (i & 7)) != 0)

    def positive_int_vector_packed(self, vec: List[int]) -> None:
        """Write a packed 3D vector of positive integers.
        
        Args:
            vec: List of [x, y, z] integer values.
        """
        self.int_packed(vec[0])
        self.int_packed(vec[1])
        self.int_packed(vec[2])

    def int_vector_packed(self, vec: List[int]) -> None:
        """Write a packed 3D vector of signed integers.
        
        Args:
            vec: List of [x, y, z] signed integer values.
        """
        f = lambda x : (abs(x) << 1) | (1 if x > 0 else 0)
        self.int_packed(f(vec[0]))
        self.int_packed(f(vec[1]))
        self.int_packed(f(vec[2]))

    def i32(self, val: int) -> None:
        """Write a signed 32-bit integer.
        
        Args:
            val: Value to write.
        """
        self.buffer.write(val.to_bytes(4, "little", signed=True))

    def array_bits(self, arr: Union[List[Any], Dict[Any, Any]], func: Callable[[Any], None]) -> None:
        """Write an array with bit-packed size.
        
        Args:
            arr: List or Dict to write.
            func: Function to write each element.
        """
        l = len(arr)
        self.u32_bits(l)
        
        if isinstance(arr, dict):
             for item in arr.items():
                 func(item)
        else:
            for item in arr:
                func(item)

    def string_bits(self, val: str) -> None:
        """Write a string with bit-packed length.
        
        Args:
            val: String to write.
        """
        self.u32_bits(len(val) + 1)
        for char in val.encode('utf-8'):
            self.bits(char, 8)
        self.bits(0, 8)