# SPDX-FileCopyrightText: 2021 Melissa LeBlanc-Williams for Adafruit Industries
#
# SPDX-License-Identifier: MIT

from machine import I2C
import sys
import time

class MagicI2C(I2C):
    """
    Extended version of I2C so it can work with the CircuitPython lib we are using.
    See:
    https://raw.githubusercontent.com/adafruit/Adafruit_Blinka/main/src/adafruit_blinka/microcontroller/generic_micropython/i2c.py
    https://github.com/adafruit/Adafruit_Blinka/blob/main/src/busio.py
    shared-bindings/busio/I2C.c
    """
    MASTER = 0

    # pylint: disable=unused-argument
    def writeto_then_readfrom(
            self, address: int, out_buffer, in_buffer, *,
            out_start: int = 0, out_end: int = sys.maxsize, in_start: int = 0,
            in_end: int = sys.maxsize):
        time.sleep(1)
        raise Exception("nah")
        print(f"Called with {address}, {out_buffer[0]} {out_buffer}, {in_buffer}, {out_start}, {out_end}, {in_start}, {in_end}")
        print(f"Slices: {out_buffer[out_start:out_end]} {in_buffer[in_start:in_end]} - size {len(in_buffer[in_start:in_end])}")
        self.writeto(address, out_buffer[out_start:out_end])
        self.readfrom_into(address, in_buffer[in_start:in_end])
        print(f"Resulting value after call is {in_buffer}")
    # pylint: enable=unused-argument
