# SPDX-FileCopyrightText: 2021 Melissa LeBlanc-Williams for Adafruit Industries
#
# SPDX-License-Identifier: MIT

from machine import I2C

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
    def __init__(self, *args, **kwargs)
        I2C.__init__(*args, **kwargs)


    # pylint: enable=unused-argument
