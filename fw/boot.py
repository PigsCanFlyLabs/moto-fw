import machine
import micropython
import time
from lsm.lsm6ds import AccelRange, LSM6DS3TRC
from machine import Pin
from magici2c import MagicI2C
import uasyncio
import os
from UARTBluetooth import UARTBluetooth
import ustruct


micropython.alloc_emergency_exception_buf(200)
print("Allocated buffer for ISR failure.")

print("Setting up accelerometer.")
i2c = MagicI2C(sda=Pin(4), scl=Pin(5))
devices = []

while len(devices) < 1:
   devices = i2c.scan()
   #time.sleep(1)
   print(f"kk!: {devices}")

device_id = devices[0]
if 107 in devices:
   device_id = 107

# Note: sometimes we also have a DS33TRC but besides the ped its the
# same so w/e, we just YOLO on the chip ids.
accel = LSM6DS3TRC(i2c, device_id)

print("Setting up callibration/logging.")
files = os.listdir()


# 1 int 12 floats
# first int -- version
# first 3 -- accel startup val
# second 3 -- gyro startup val
# third 3 -- inital accel val
# fourth 3 -- inital gyro val
power_on_gyro = accel.gyro
# At (first) power on the accelerometer gives us a good idea of the direction
# of gravity (since we are not moving yet).
power_on_accel = accel.acceleration
initial_min_ms_delta = 4
new_accel = []
new_gyro = []

calib_struct = "iffffffffffff"
calib_version = 1
rlen = ustruct.calcsize(calib_struct)
calib_buf = bytearray(rlen)
calibration_data = None

def abs(x):
   if (x < 0):
      return -x
   return x

def do_calib():
   # Wait for inital acceleration
   # See URL:http://dx.doi.org/10.19044/esj.2018.v14n9p372
   delta = 0
   new_accel = accel.acceleration
   new_gyro = accel.gyro
   # Ignore the one axis that is mostly gravity
   max_v = 0
   probably_gravity_axis = 0
   for i in range(0, 3):
      if abs(power_on_accel[i]) > abs(max_v):
         probably_gravity_axis = i
         max_v = power_on_accel[i]
   axis = list(range(0, 3))
   # Note this is mutating and it returns a nonetype.
   axis.remove(probably_gravity_axis)
   while (delta < initial_min_ms_delta):
      new_accel = accel.acceleration
      new_gyro = accel.gyro
      delta = 0
      for i in axis:
         delta += abs(new_accel[i] - power_on_accel[i])
      print(f"Current delta is {delta} with {new_accel}")
               
   calibration_data = [calib_version] 
   calibration_data.extend(power_on_accel)
   calibration_data.extend(power_on_gyro)
   calibration_data.extend(new_accel)
   calibration_data.extend(new_gyro)
   with open("calib", "wb") as f:
      ustruct.pack_into(calib_struct, calib_buf, 0, *calibration_data)
      f.write(calib_buf)

def load_calib():
   with open("calib", "rb") as f:
      f.readinto(calib_buf)
      ustruct.unpack_from(calib_struct, calib_buf)
   # If we have a different version redocollaboration
   if calib_buf[0] != calib_version:
      print(f"Calibration version mismatch (e.g. {calib_struct[0]} != {calib_version})")
      #time.sleep(1)
      do_calib()
   else:
      power_on_accel = calib_struct[1:4]
      power_on_gyro = calib_struct[4:7]
      new_accel = calib_struct[7:10]
      new_gyro = calib_struct[10:13]
   
if "calib" not in files:
   print("No calibration found.")
   #time.sleep(1)
   do_calib()
else:
   try:
      load_calib()
   except Exception as e:
      print(f"Error {e} trying to load calibration?")
      #time.sleep(1)
      do_calib()


if "farts" not in files:
   os.mkdir("farts")

existing_file_ids = list(map(lambda x: int(x), os.listdir("farts")))
file_id = 0
if len(existing_file_ids) == 0:
    file_id = 0
else:
    file_id = existing_file_ids[-1] + 1

log_file = None
if (file_id < 10):
   log_file = open(f"farts/{file_id}", "w")
else:
   print("Skipping logging we already have 10 log files.")

print(f"Using file id {file_id}")

light_off = 0
light_on = 0

def brakelight_changed(pin):
    """
    Detect when the brake light is triggered (on or off)
    """
    global light_off
    global light_on
    if pin.value() == 0:
        light_off = 1
    else:
        light_on = 1


print("Setting up brakelight hardware.")
brakelight_trigger_pin = Pin(0)
brakelight_detect_pin = Pin(1)
brakelight_detect_pin.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=brakelight_changed)


async def log_brakelight():
   """
   Log Brakelight status
   """
   global light_off
   global light_on
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


async def log_accel():
   c = 0
   while True:
      c = c + 1
      await uasyncio.sleep(0.20)
      # Only log the first 10k times
      if (c < 10000 and log_file is not None):
         log_file.write(f"g:{accel.gyro}")
         log_file.write(f"a:{accel.acceleration}")
         if c % 100 == 0:
            log_file.flush()
      if c % 10 == 0:
         print(f"g:{accel.gyro}")
         print(f"a:{accel.acceleration}")

async def trigger_light():
   while True:
      c = accel.acceleration


async def main():
   uasyncio.create_task(log_brakelight())
   uasyncio.create_task(log_accel())
   while True:
      await uasyncio.sleep(1)

UARTBluetooth("PCF GB")

# Kick off the main loop
uasyncio.run(main())
