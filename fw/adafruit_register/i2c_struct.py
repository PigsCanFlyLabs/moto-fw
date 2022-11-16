# SPDX-FileCopyrightText: 2016 Scott Shawcroft for Adafruit Industries
#
# SPDX-License-Identifier: MIT
# pylint: disable=too-few-public-methods

"""
`adafruit_register.i2c_struct`
====================================================

Generic structured registers based on `struct`

* Author(s): Scott Shawcroft
"""

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_Register.git"

import struct

try:
    from typing import Optional, Type, Tuple, Any, NoReturn
    from circuitpython_typing.device_drivers import I2CDeviceDriver
except ImportError:
    pass


class Struct:
    """
    Arbitrary structure register that is readable and writeable.

    Values are tuples that map to the values in the defined struct.  See struct
    module documentation for struct format string and its possible value types.

    :param int register_address: The register address to read the bit from
    :param str struct_format: The struct format string for this register.
    """

    def __init__(self, register_address: int, struct_format: str) -> None:
        self.format = struct_format
        self.buffer = bytearray(struct.calcsize(self.format))
        self.register_address = register_address

    def __get__(
        self,
        obj: Optional[I2CDeviceDriver],
        objtype: Optional[Type[I2CDeviceDriver]] = None,
    ) -> Tuple:
        with obj.i2c_device as i2c:
            i2c.readfrom_mem_into(self.register_address, self.buffer)
        return struct.unpack_from(self.format, self.buffer)

    def __set__(self, obj: I2CDeviceDriver, value: Tuple) -> None:
        struct.pack_into(self.format, self.buffer, 0, *value)
        with obj.i2c_device as i2c:
            i2c.writeto_mem_into(self.register_address, self.buffer)


class UnaryStruct:
    """
    Arbitrary single value structure register that is readable and writeable.

    Values map to the first value in the defined struct.  See struct
    module documentation for struct format string and its possible value types.

    :param int register_address: The register address to read the bit from
    :param str struct_format: The struct format string for this register.
    """

    def __init__(self, register_address: int, struct_format: str) -> None:
        self.format = struct_format
        self.address = register_address

    def __get__(
        self,
        obj: Optional[I2CDeviceDriver],
        objtype: Optional[Type[I2CDeviceDriver]] = None,
    ) -> Any:
        buf = bytearray(struct.calcsize(self.format))
        with obj.i2c_device as i2c:
            i2c.readfrom_mem_into(self.address, buf)
        return struct.unpack_from(self.format, buf)[0]

    def __set__(self, obj: I2CDeviceDriver, value: Any) -> None:
        buf = bytearray(struct.calcsize(self.format))
        struct.pack_into(self.format, buf, 0, value)
        with obj.i2c_device as i2c:
            i2c.writeto_mem(self.address, buf)


class ROUnaryStruct(UnaryStruct):
    """
    Arbitrary single value structure register that is read-only.

    Values map to the first value in the defined struct.  See struct
    module documentation for struct format string and its possible value types.

    :param int register_address: The register address to read the bit from
    :param type struct_format: The struct format string for this register.
    """

    def __set__(self, obj: I2CDeviceDriver, value: Any) -> NoReturn:
        raise AttributeError()
