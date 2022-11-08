include("$(BOARD_DIR)/../manifest.py")


freeze(".",
       ("boot.py",
        "magici2c.py",
       ),
)
package("lsm")
package("adafruit_bus_device")
package("adafruit_register")
