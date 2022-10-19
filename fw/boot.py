import micropython
import time
from LSM6DS3TR import LSM6DS3TR
from machine import I2C

micropython.alloc_emergency_exception_buf(200)
print("Allocated buffer for ISR failure.")
time.sleep(1)
print("Waiting to allow debugger to attach....")
time.sleep(1)
print("Continuing pandas :D")

i2c = I2C()

devices = LSM6DS3TR(i2c)

while True:
    time.sleep(1)
    print(f"kk!: {devices}")
