import machine
import micropython
import time
from lsm.lsm6ds import AccelRange, LSM6DS3TRC
from machine import Pin
from magici2c import MagicI2C
import uasyncio
import os
from UARTBluetooth import UARTBluetooth


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

if "farts" not in os.listdir():
   os.mkdir("farts")

existing_file_ids = list(map(lambda x: int(x), os.listdir("farts")))
file_id = 0
if len(existing_file_ids) == 0:
    file_id = 0
else:
    file_id = existing_file_ids[-1] + 1
 
log_file = open(f"farts/{file_id}", "w")

print(f"Using file id {file_id}")

light_off = 0
light_on = 0

def break_light_changed(pin):
    """
    Detect when the break light is triggered (on or off)
    """
    if pin.value() == 0:
        light_off = 1
    else:
        light_on = 1


print("Setting up hardware.")
breaklight_trigger_pin = Pin(0)
breaklight_detect_pin = Pin(1)
breaklight_detect_pin.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=break_light_changed)
i2c = MagicI2C(sda=Pin(4), scl=Pin(5))
devices = []

while len(devices) < 1:
   devices = i2c.scan()
   time.sleep(1)
   print(f"kk!: {devices}")

device_id = devices[0]
if 107 in devices:
   device_id = 107

# Note: sometimes we also have a DS33TRC but besides the ped its the
# same so w/e, we just YOLO on the chip ids.
accel = LSM6DS3TRC(i2c, device_id)


async def log_breaklight():
   """
   Log Breaklight status
   """
   while True:
      if light_off > 0:
         print("Rise!")
         light_off = 0
         log_file.write("rise")
      if light_on > 0:
         print("fall")
         light_on = 0
         log_file.write("fall")
      await uasyncio.sleep(0.01)

async def main():
   while True:
      await uasyncio.sleep(0.5)
      log_file.write(f"g:{accel.gyro}")
      log_file.write(f"a:{accel.acceleration}")
      if c % 10 == 0:
         print(f"g:{accel.gyro}")
         print(f"a:{accel.acceleration}")

UARTBluetooth("PCF GB")

# Kick off the main loop
uasyncio.run(main())
