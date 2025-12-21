"""Binary reader for Brickadia save files.

This module provides the Reader class for deserializing Brickadia save files
from binary format, supporting both byte and bit-level operations.
"""
import uuid
import struct
import zlib
from datetime import datetime, timedelta
from typing import Any, Callable, List, TypeVar, Union
from .user import User, BrickOwner
from .utils import ue4_basetime
from .color import Color
from .bits import BitBuffer, Bytes

T = TypeVar('T')


class Reader:
    """Binary reader for deserializing Brickadia save file data.
    
    Attributes:
        buffer: The underlying buffer to read from.
    """
    
    def __init__(self, buffer: Union[Bytes, BitBuffer, Any]) -> None:
        """Initialize a Reader with a buffer.
        
        Args:
            buffer: Buffer to read from (Bytes, BitBuffer, or file-like object).
        """
        self.buffer = buffer

    def read(self, size: int) -> bytes:
        """Read raw bytes from the buffer.
        
        Args:
            size: Number of bytes to read.
            
        Returns:
            Bytes read from the buffer.
        """
        return self.buffer.read(size)

    def read_bit(self) -> bool:
        """Read a single bit from the buffer.
        
        Returns:
            Boolean value of the bit.
        """
        return self.buffer.read_bit()

    def byte_align(self) -> None:
        """Align the read position to the next byte boundary."""
        self.buffer.byte_align()

    def read_compressed(self) -> BitBuffer:
        """Read and decompress a compressed data section.
        
        Returns:
            BitBuffer containing the decompressed data.
        """
        uncompressed_len = self.u32()
        compressed_len = self.u32()
        if compressed_len != 0:
            return BitBuffer(zlib.decompress(self.read(compressed_len), bufsize=uncompressed_len))
        else:
            return BitBuffer(self.buffer.read(uncompressed_len))

    def u8(self) -> int:
        """Read an unsigned 8-bit integer.
        
        Returns:
            Unsigned 8-bit integer value.
        """
        return int.from_bytes(self.buffer.read(1), byteorder="little", signed=False)

    def u16(self) -> int:
        """Read an unsigned 16-bit integer.
        
        Returns:
            Unsigned 16-bit integer value.
        """
        return int.from_bytes(self.buffer.read(2), byteorder="little", signed=False)

    def u32(self) -> int:
        """Read an unsigned 32-bit integer.
        
        Returns:
            Unsigned 32-bit integer value.
        """
        return int.from_bytes(self.buffer.read(4), byteorder="little", signed=False)

    def i32(self) -> int:
        """Read a signed 32-bit integer.
        
        Returns:
            Signed 32-bit integer value.
        """
        return int.from_bytes(self.buffer.read(4), byteorder="little", signed=True)

    def u64(self) -> int:
        """Read an unsigned 64-bit integer.
        
        Returns:
            Unsigned 64-bit integer value.
        """
        return int.from_bytes(self.buffer.read(8), byteorder="little", signed=False)

    def u32_bits(self) -> int:
        """Read a 32-bit unsigned integer from bit stream.
        
        Returns:
            Unsigned 32-bit integer value.
        """
        arr = self.bits(32)
        return arr[3] << 24 | arr[2] << 16 | arr[1] << 8 | arr[0]

    def bits(self, size: int) -> List[int]:
        """Read a sequence of bits as bytes.
        
        Args:
            size: Number of bits to read (must be multiple of 8).
            
        Returns:
            List of bytes containing the bits.
        """
        dst = [0 for v in range(int(size/8))]
        for bit in range(size):
            shift = bit & 0x7
            dst[bit >> 3] = (dst[bit >> 3] & ~(1 << shift)) | ((1 if self.read_bit() else 0) << shift)
        return dst

    def int_max(self, max_val: int) -> int:
        """Read a variable-length integer with a maximum value.
        
        Args:
            max_val: Maximum possible value.
            
        Returns:
            Integer value read.
        """
        val = 0
        mask = 1
        while val + mask < max_val:
            if self.buffer.read_bit():
                val |= mask
            mask = mask << 1
        return val



    def ascii(self, size: int) -> str:
        """Read an ASCII string.
        
        Args:
            size: Length of the string including null terminator.
            
        Returns:
            Decoded ASCII string.
        """
        ascii_str = self.buffer.read(size-1).decode('utf-8')
        self.buffer.read(1)
        return ascii_str

    def ucs2(self, size: int) -> str:
        """Read a UCS-2 (UTF-16) string.
        
        Args:
            size: Negative length indicator for UCS-2 string.
            
        Returns:
            Decoded UCS-2 string.
            
        Raises:
            ValueError: If size is not a valid UCS-2 size.
        """
        size = -size
        if size % 2 != 0:
            raise ValueError(f"Invalid UCS-2 size: {size}. Must be even.")
        ucs2_str = self.buffer.read(size-2).decode('utf-16')
        self.buffer.read(2)
        return ucs2_str

    def string(self) -> str:
        """Read a string (ASCII or UCS-2).
        
        Returns:
            Decoded string.
        """
        strlen = self.i32()
        if strlen >= 0:
            return self.ascii(strlen)
        else:
            return self.ucs2(strlen)

    def id(self) -> uuid.UUID:
        """Read a UUID.
        
        Returns:
            UUID object.
        """
        bytes_be = b''
        for _ in range(4):
            be = bytearray(self.buffer.read(4))
            be.reverse()
            bytes_be += be

        return uuid.UUID(bytes=bytes_be)

    def user_name_first(self) -> User:
        """Read a User with name before ID.
        
        Returns:
            User object.
        """
        name = self.string()
        id = self.id()
        return User(name, id)

    def brick_owner(self) -> BrickOwner:
        """Read a BrickOwner.
        
        Returns:
            BrickOwner object.
        """
        id = self.id()
        name = self.string()
        brickcount = self.u32()
        return BrickOwner(name, id, brickcount)

    def datetime(self) -> datetime:
        """Read a datetime value.
        
        Returns:
            datetime object.
        """
        ticks = self.u64()
        micro = ticks / 10
        nano = (ticks % 10) * 100
        return ue4_basetime() + timedelta(microseconds=micro) + timedelta(microseconds=nano/1000)

    def color(self) -> Color:
        """Read a Color value.
        
        Returns:
            Color object.
        """
        return Color(self.u32())

    def array(self, func: Callable[[], T]) -> List[T]:
        """Read an array of values.
        
        Args:
            func: Function to read each element.
            
        Returns:
            List of values.
        """
        size = self.u32()
        vals = []
        for _ in range(size):
            vals.append(func())
        return vals

    def array_bits(self, func: Callable[[], T]) -> List[T]:
        """Read an array of values with bit-packed size.
        
        Args:
            func: Function to read each element.
            
        Returns:
            List of values.
        """
        size = self.u32_bits()
        vals = []
        for _ in range(size):
            vals.append(func())
        return vals

    def int_packed(self) -> int:
        """Read a packed integer value.
        
        Returns:
            Unpacked integer value.
        """
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

    def positive_int_vector_packed(self) -> List[int]:
        """Read a packed 3D vector of positive integers.
        
        Returns:
            List of [x, y, z] integer values.
        """
        return [self.int_packed(), self.int_packed(), self.int_packed()]

    def signed_int_packed(self) -> int:
        """Read a packed signed integer.
        
        Returns:
            Signed integer value.
        """
        val = self.int_packed()
        return (val >> 1) if ((val & 1) != 0) else -(val >> 1)

    def int_vector_packed(self) -> List[int]:
        """Read a packed 3D vector of signed integers.
        
        Returns:
            List of [x, y, z] signed integer values.
        """
        return [self.signed_int_packed(), self.signed_int_packed(), self.signed_int_packed()]

    def string_bits(self) -> str:
        """Read a bit-packed string.
        
        Returns:
            Decoded string.
        """
        size = self.u32_bits()
        stuff = self.bits(size * 8 - 8)
        self.bits(8)
        return ''.join([chr(c) for c in stuff])

    def float_bits(self) -> float:
        """Read a bit-packed float value.
        
        Returns:
            Float value.
        """
        bits = self.bits(32)
        arr = b''
        for bit in bits:
            arr += bit.to_bytes(1, 'little')
        return struct.unpack('f', arr)[0]

    def unreal(self, val_type: str) -> Any:
        """Read an Unreal Engine property value.
        
        Args:
            val_type: Type of the property ('Class', 'Object', 'Boolean', 'Float', 'Color', 'Byte', 'Rotator').
            
        Returns:
            Property value of appropriate type.
        """
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
