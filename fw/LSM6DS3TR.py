class LSM6DS3TR():
    """
    A sketchy implementation for talking to an LSM6DS3TR using I2C
    """

    def __init__(self, I2C_device, i2c_addr=None):
        self.i2c = I2C_device
        i2c_ids = self.i2c.scan()
        print(f"Found devices {i2c_ids}")
        return i2c_ids
