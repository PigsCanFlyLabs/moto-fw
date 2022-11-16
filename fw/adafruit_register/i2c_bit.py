# SPDX-FileCopyrightText: 2016 Scott Shawcroft for Adafruit Industries
#
# SPDX-License-Identifier: MIT
# pylint: disable=too-few-public-methods

"""
`adafruit_register.i2c_bit`
====================================================
Single bit registers
* Author(s): Scott Shawcroft
"""

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_Register.git"

try:
    from typing import Optional, Type, NoReturn
except ImportError:
    pass


class RWBit:
    """
    Single bit register that is readable and writeable.
    Values are `bool`
    :param int register_address: The register address to read the bit from
    :param int bit: The bit index within the byte at ``register_address``
    :param int register_width: The number of bytes in the register. Defaults to 1.
    """

    def __init__(
        self,
        register_address: int,
        bit: int,
        register_width: int = 1,
    ) -> None:
        self.bit_mask = 1 << (bit % 8)  # the bitmask *within* the byte!
        self.buffer = bytearray(register_width)
        self.register_address = register_address
        self.byte = bit // 8  # the byte number within the buffer

    def __get__(
        self,
        obj: Optional,
        objtype: Optional = None,
    ) -> bool:
        print(f"Pre-Read Buffer is {self.buffer}")
        with obj.i2c_device as i2c:
            i2c.readfrom_mem_into(self.register_address, self.buffer)
        print(f"Post read Buffer is {self.buffer}")
        return bool(self.buffer[self.byte] & self.bit_mask)

    def __set__(self, obj, value: bool) -> None:
        with obj.i2c_device as i2c:
            print(f"Pre-Read-Set Buffer is {self.buffer}")
            i2c.readfrom_mem_into(self.register_address, self.buffer)
            print(f"Pre-Set Buffer is {self.buffer}")
            if value:
                self.buffer[self.byte] |= self.bit_mask
            else:
                self.buffer[self.byte] &= ~self.bit_mask
            i2c.writeto_mem_into(self.register_address, self.buffer)


class ROBit(RWBit):
    """Single bit register that is read only. Subclass of `RWBit`.
    Values are `bool`
    :param int register_address: The register address to read the bit from
    :param type bit: The bit index within the byte at ``register_address``
    :param int register_width: The number of bytes in the register. Defaults to 1.
    """

    def __set__(self, obj, value: bool) -> NoReturn:
        raise AttributeError()
