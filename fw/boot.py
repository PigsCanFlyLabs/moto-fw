import machine
import micropython
import time
from lsm.lsm6ds import LSM6DS3TRC
from machine import Pin
from magici2c import MagicI2C

micropython.alloc_emergency_exception_buf(200)
print("Allocated buffer for ISR failure.")
time.sleep(1)
print("Waiting to allow debugger to attach....")
time.sleep(1)
print("Continuing pandas :D")

time.sleep(1)
print("Sleeeeeeeping some more.")

time.sleep(1)
print("Sleeeeeeeping some more.")


i2c = MagicI2C(sda=Pin(4), scl=Pin(5))

devices = []

while len(devices) < 1:
    devices = i2c.scan()
    time.sleep(1)
    print(f"kk!: {devices}")

accel = LSM6DS3TRC(i2c, devices[0])
