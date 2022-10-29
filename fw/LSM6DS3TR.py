
# Constants from https://github.com/adafruit/Adafruit_CircuitPython_LSM6DS/blob/main/adafruit_lsm6ds/__init__.py
# See descriptions of registers https://www.st.com/resource/en/application_note/an5130-lsm6ds3trc-alwayson-3d-accelerometer-and-3d-gyroscope-stmicroelectronics.pdf
_LSM6DS_MLC_INT1 = const(0x0D)
_LSM6DS_WHOAMI = const(0xF)
_LSM6DS_CTRL1_XL = const(0x10)
_LSM6DS_CTRL2_G = const(0x11)
_LSM6DS_CTRL3_C = const(0x12)
_LSM6DS_CTRL8_XL = const(0x17)
_LSM6DS_CTRL9_XL = const(0x18)
_LSM6DS_CTRL10_C = const(0x19)
_LSM6DS_ALL_INT_SRC = const(0x1A)
_LSM6DS_OUT_TEMP_L = const(0x20)
_LSM6DS_OUTX_L_G = const(0x22)
_LSM6DS_OUTX_L_A = const(0x28)
_LSM6DS_MLC_STATUS = const(0x38)
_LSM6DS_STEP_COUNTER = const(0x4B)
_LSM6DS_TAP_CFG0 = const(0x56)
_LSM6DS_TAP_CFG = const(0x58)
_LSM6DS_MLC0_SRC = const(0x70)
_MILLI_G_TO_ACCEL = 0.00980665
_TEMPERATURE_SENSITIVITY = 256
_TEMPERATURE_OFFSET = 25.0

_LSM6DS_EMB_FUNC_EN_A = const(0x04)
_LSM6DS_EMB_FUNC_EN_B = const(0x05)
_LSM6DS_FUNC_CFG_ACCESS = const(0x01)
_LSM6DS_FUNC_CFG_BANK_USER = const(0)
_LSM6DS_FUNC_CFG_BANK_HUB = const(1)
_LSM6DS_FUNC_CFG_BANK_EMBED = const(2)



class LSM6DS3TR():
    """
    A sketchy implementation for talking to an LSM6DS3TR using I2C
    """

    # I think we only need RANGE_2G and _maybe_ 4G but uncomment for others.
    AccelRange = {
        2: [0, 0.061],
#        16: [1, 0.488],
        4: [2, 0.122],
#        8: [3, 0.244],
    }

    def __init__(self, I2C_device, i2c_addr=None):
        self.i2c = I2C_device
        i2c_ids = self.i2c.scan()
        print(f"Found devices {i2c_ids}")
        self.device_id = i2c_ids[0] # meh...
        # Setup the range, we use 2G because breaking is rarely above 1G
        self.set_accel_range("2G")
        self._ctrl1_xl_value = b''
        return i2c_ids

    def set_accel_range(_range: int):
        self.i2c.writeto_mem(self.device_id, _LSM6DS_CTRL1_XL, _range)

    def _raw_accel(self):
        return self.i2c.readfrom_mem(self.device_id, _LSM6DS_OUTX_L_A, 2)

    def acceleration(self) -> Tuple[float, float, float]:
        x = self._scale_accel(accel[0])
        y = self._scale_accel(accel[1])
        z = self._scale_accel(accel[2])

        return (x, y, z)

    def _scale_accel(self, raw_measurement: int) -> float:
        return (
            raw_measurement
            * self.AccelRange[self._cached_accel_range]
            * _MILLI_G_TO_ACCEL
        )
