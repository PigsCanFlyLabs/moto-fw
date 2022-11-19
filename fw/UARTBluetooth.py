import micropython
import uasyncio

_BMS_MTU = 128


class UARTBluetooth():

    def __init__(self, name: str):
        print("Starting UART BLuetooth interface.")
        self.name = name
        import bluetooth
        try:
            import mac_setup
            mac_bits = 1
            print(dir(mac_setup))
            mac_setup.setup(mac_bits)
        except Exception as e:
            print(help('modules'))
            print(f"Weird error {e} trying to configure MAC prefix, will use ESP32 prefix")
        self.ble = bluetooth.BLE()
        self.services = ()
        self.service_uuids = []
        self.conn_handle = 0
        print("Enable.")
        self.enable()
        self.target_length = 0
        self.mtu = 10
        self.msg_buffer = bytearray(1000)
        self.mv_msg_buffer = memoryview(self.msg_buffer)
        self.msg_buffer_idx = 0
        # Setup a call-back for ble msgs
        self.ble.irq(self.ble_irq)
        print("Prepairing to register")
        self.register()
        print("Prepairing to advertise.")
        self.advertise()
        print("Ok!")
        self._send_logs_ref = self.send_logs

    def send_logs(self, *args):
        """Send the logs. Ignores *args but present because schedule
        requires some args."""
        import os
        existing_files = os.listdir("farts")
        for file_name in existing_files:
            full_filename = f"farts/{file_name}"
            with open(full_filename, "r") as log_file:
                for line in log_file.readlines():
                    self.send(line)
            os.unlink(full_filename)
            
            

    def enable(self):
        self.ble.config(gap_name=self.name)
        self.ble.active(True)
        print(f"BLE MAC address is {self.ble.config('mac')}")
        self.ble.config(gap_name=self.name)

    def disable(self):
        self.ble.config(gap_name=self.name)
        self.ble.active(False)
        self.ble.config(gap_name=self.name)

    def ble_irq(self, event: int, data):
        """Handle BlueTooth Event."""
        print(f"Handling {event} {data}")
        print(f"DEBUG: Current event loop task is {uasyncio.current_task()}")
        print(f"DEBUG: state: {uasyncio.current_task().state}")
        print(str(event))
        print(str(data))
        # Handle bluetooth events
        if event == 1:
            # Paired
            self.connected = True
            conn_handle, _, _ = data
            self.conn_handle = conn_handle
            micropython.schedule(self._send_logs_ref, [])


    def register(self):
        """Register nordic UART service."""

        import bluetooth
        # Nordic UART Service (NUS)
        NUS_UUID = '6E400001-B5A3-F393-E0A9-E50E24DCCA9E'
        RX_UUID = '6E400002-B5A3-F393-E0A9-E50E24DCCA9E'
        TX_UUID = '6E400003-B5A3-F393-E0A9-E50E24DCCA9E'

        BLE_NUS = bluetooth.UUID(NUS_UUID)
        BLE_RX = (bluetooth.UUID(RX_UUID), bluetooth.FLAG_WRITE)
        BLE_TX = (bluetooth.UUID(TX_UUID), bluetooth.FLAG_READ | bluetooth.FLAG_NOTIFY)

        BLE_UART = (BLE_NUS, (BLE_TX, BLE_RX,))
        SERVICES = (BLE_UART, )
        self.services = SERVICES
        self.service_uuids = [BLE_NUS]
        ((self.tx, self.rx,), ) = self.ble.gatts_register_services(SERVICES)
        rxbuf = 500
        self.ble.gatts_set_buffer(self.rx, rxbuf, True)

    def send(self, data):
        try:
            print(f"Preparing to send {data} to UART BTLE.")
            # Send how many bytes were going to have, we always use 4 bytes to send this.
            self.ble.gatts_notify(self.conn_handle, self.tx, int.to_bytes(len(data), 4, 'little'))
            # Send all of the bytes
            idx = 0
            while (idx < len(data)):
                self.ble.gatts_notify(self.conn_handle, self.tx, data[idx:idx + self.mtu])
                idx = idx + self.mtu
            print("Done.")
        except Exception as e:
            print(f"Failed to send {data} to UART BTLE - {e}")
            # TODO: Better exception handling?

    def advertise(self):
        print(f"Advertising {self.name}")
        from micropython import const
        import struct
        device_type = 5184  # Generic outdoor
        # Generate a payload to be passed to gap_advertise(adv_data=...).
        # From:
        # https://github.com/micropython/micropython/blob/master/examples/bluetooth/
        # This is MIT licensed.

        def advertising_payload(limited_disc=False, br_edr=False, name=None, services=None,
                                appearance=0):
            _ADV_TYPE_FLAGS = const(0x01)
            _ADV_TYPE_NAME = const(0x09)
            _ADV_TYPE_UUID16_COMPLETE = const(0x3)
            _ADV_TYPE_UUID32_COMPLETE = const(0x5)
            _ADV_TYPE_UUID128_COMPLETE = const(0x7)
            _ADV_TYPE_APPEARANCE = const(0x19)

            payload = bytearray()

            def _append(adv_type, value):
                nonlocal payload
                payload += struct.pack("BB", len(value) + 1, adv_type) + value

            _append(
                _ADV_TYPE_FLAGS,
                struct.pack("B", (0x01 if limited_disc else 0x02) + (0x18 if br_edr else 0x04)),
            )

            if name:
                _append(_ADV_TYPE_NAME, name)

            if services:
                print("Adding services to advertising payload.")
                for uuid in services:
                    print(f"Service {uuid} in {services}")
                    # Return here and fix the cast issue.
                    b = bytes(uuid)
                    if len(b) == 2:
                        _append(_ADV_TYPE_UUID16_COMPLETE, b)
                    elif len(b) == 4:
                        _append(_ADV_TYPE_UUID32_COMPLETE, b)
                    elif len(b) == 16:
                        _append(_ADV_TYPE_UUID128_COMPLETE, b)

            # See org.bluetooth.characteristic.gap.appearance.xml
            if appearance:
                _append(_ADV_TYPE_APPEARANCE, struct.pack("<h", appearance))

            return payload

        print("Creating advertise payload")
        print(self.name)
        print("Service UUIDs:")
        print(self.service_uuids)
        print("Device type")
        print(device_type)
        _payload = advertising_payload(
            name=self.name,
            services=self.service_uuids,
            appearance=device_type)
        try:
            print("Created payload :)")
            self.ble.gap_advertise(
                100,
                _payload,
                resp_data=_payload)
        except Exception as e:
            print(f"Error using long payload for BTLE {e}")
            _short_payload = advertising_payload(
                name=self.name,
                services=[],
                appearance=device_type)
            try:
                print("Advertising short payload :)")
                self.ble.gap_advertise(
                    100,
                    _short_payload,
                    resp_data=_payload)
            except Exception as e:
                print(f"Error using long resp payload - {e}")
                self.ble.gap_advertise(
                    100,
                    _short_payload,
                    resp_data=_short_payload)
