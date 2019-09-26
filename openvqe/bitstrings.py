from enum import Enum
from typing import List
from functools import total_ordering

class BitNumbering(Enum):
    LSB = 0  # least signigicant bit ordering:  1 -> 0b01 -> [1,0] i.e bit0 is the least significant
    MSB = 1  # Most  significant bit ordering:  1 -> 0b01 -> [0,1] i.e bit0 is the most significant
    # MSB is the default

@total_ordering
class BitString:
    """
    Bitstring Class
    All Bitstrings are stored as integers
    return them as integers, binary strings or arrays of integers
    """

    @property
    def numbering(self) -> BitNumbering:
        return BitNumbering.MSB

    @property
    def nbits(self):
        return self._nbits

    @nbits.setter
    def nbits(self, value):
        self._nbits = value
        self.update_nbits()

    def update_nbits(self):
        current = self._nbits
        min_needed = len(format(self._value, 'b'))
        self._nbits = max(current, min_needed)
        return self

    @property
    def binary(self):
        if self.numbering is BitNumbering.MSB:
            return format(self._value, 'b').zfill(self.nbits)
        else:
            return format(self._value, 'b').zfill(self.nbits)[::-1]

    @binary.setter
    def binary(self, other: str):
        assert (isinstance(other, str))
        if other.startswith('0b'):
            other = other[2:]
        if self.numbering == BitNumbering.LSB:
            self._value = int(other[::-1], 2)
        else:
            self._value = int(other, 2)
        self.update_nbits()
        return self

    @property
    def integer(self):
        return self._value

    @integer.setter
    def integer(self, other: int):
        self._value = other
        self.update_nbits()
        return self

    @property
    def array(self):
        return [int(i) for i in self.binary]

    @array.setter
    def array(self, other):
        if self.numbering == BitNumbering.MSB:
            self.integer = int("".join(str(x) for x in other), 2)
        else:
            self.integer = int("".join(str(x) for x in reversed(other)), 2)
        self.update_nbits()
        return self

    def __init__(self, nbits: int = 0):
        self._value = None
        self._nbits = nbits

    @classmethod
    def from_array(cls, array: list, nbits: int = 0):
        if isinstance(array, cls):
            return cls.from_bitstring(other=array)
        result = cls(nbits=nbits)
        result.array = array
        return result

    @classmethod
    def from_int(cls, integer: int, nbits: int = 0):
        if isinstance(integer, cls):
            return cls.from_bitstring(other=integer)
        result = cls(nbits=nbits)
        result.integer = integer
        return result

    @classmethod
    def from_binary(cls, binary: str, nbits: int = 0):
        if isinstance(binary, cls):
            return cls.from_bitstring(other=binary)
        result = cls(nbits=nbits)
        result.binary = binary
        return result

    @classmethod
    def from_bitstring(cls, other):
        result = cls(nbits=other.nbits)
        result.integer = other.integer
        return result

    def __add__(self, other):
        nbits = max(self.nbits, other.nbits)
        return BitString.from_int(integer=self.integer + other.integer, nbits=nbits)

    def __iadd__(self, other):
        self.integer = self.integer + other.integer
        self.update_nbits()

    def __mul__(self, other):
        return BitString.from_int(integer=self.integer * other.integer, nbits=nbits)

    def __imul__(self, other):
        self.integer = self.integer * other.integer
        self.update_nbits()

    def __eq__(self, other) -> bool:
        if isinstance(other, int):
            return self.integer == other
        if isinstance(other, str):
            return self.binary == other
        return self.numbering == other.numbering and self._value == other._value

    def __repr__(self) -> str:
        return str(self.integer)

    def __hash__(self) -> int:
        return hash(self._value)

    def __getitem__(self, item: int) -> List[int]:
        return self.array[item]

    def __setitem__(self, key, value):
        array = self.array
        array[key] = value
        self.array = array
        return self

    def __lt__(self, other) -> bool:
        if isinstance(other, int):
            return self.integer < other
        return self.integer < other.integer


class BitStringLSB(BitString):

    @property
    def numbering(self) -> BitNumbering:
        return BitNumbering.LSB
