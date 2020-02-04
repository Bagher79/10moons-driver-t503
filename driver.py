# Proper test driver for the 10moons graphics tablet

import os

# Specification of the device https://python-evdev.readthedocs.io/en/latest/
from evdev import UInput, ecodes, AbsInfo
# Establish usb communication with device
import usb
import yaml

path = os.path.join(os.path.dirname(__file__), "config.yaml")
# Loading tablet configuration
with open(path, "r") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

pen_events = {
    ecodes.EV_KEY: [
        ecodes.BTN_TOOL_PEN,
        ecodes.BTN_TOUCH
    ],
    ecodes.EV_ABS: [
        (ecodes.ABS_X, AbsInfo(value=0, min=0, max=config['pen']['max_x'], fuzz=0, flat=0, resolution=config["pen"]["resolution_x"])),
        (ecodes.ABS_Y, AbsInfo(value=0, min=0, max=config['pen']['max_y'], fuzz=0, flat=0, resolution=config["pen"]["resolution_y"])),
        (ecodes.ABS_PRESSURE, AbsInfo(value=0, min=0, max=config['pen']['max_pressure'], fuzz=0, flat=0, resolution=0))
    ],
}

# Find the device
dev = usb.core.find(idVendor=config["vendor_id"], idProduct=config["product_id"])

if not dev:
    print("No 10moons T503 tablet is connected.")
    exit(2)

print("10moons T503 driver initialized at device found on Bus %03i Address %03i!" % (dev.bus, dev.address))
# Select end point for reading second interface [2] for actual data
# I don't know what [0] and [1] are used for
ep = dev[0].interfaces()[2].endpoints()[0]
# Reset the device (don't know why, but till it works don't touch it)
dev.reset()

# Drop default kernel driver from all devices
for j in [0, 1, 2]:
    if dev.is_kernel_driver_active(j):
        dev.detach_kernel_driver(j)

# Set new configuration
dev.set_configuration()

vpen = UInput(events=pen_events, name=config["xinput_name"], version=0x3)

pen_hovering = False

# Infinite loop
while True:
    try:
        data = dev.read(ep.bEndpointAddress, ep.wMaxPacketSize)
        if data[1] in [192, 193]: # Pen actions
            if not pen_hovering:
                # Need to emit event BTN_TOOL_PEN = 1 when pen is hovering,
                # this way the system can recognize the device as a tablet.
                # https://www.kernel.org/doc/Documentation/input/event-codes.txt
                vpen.write(ecodes.EV_KEY, ecodes.BTN_TOOL_PEN, 1)
                pen_hovering = True

            pen_x = (data[5] * 255 + data[4])
            pen_y = config['pen']['max_y'] - (data[3] * 255 + data[2])
            pen_pressure = data[7] * 255 + data[6]
            vpen.write(ecodes.EV_ABS, ecodes.ABS_X, pen_x)
            vpen.write(ecodes.EV_ABS, ecodes.ABS_Y, pen_y)
            vpen.write(ecodes.EV_ABS, ecodes.ABS_PRESSURE, pen_pressure)
            if data[1] == 193: # Pen touch
                vpen.write(ecodes.EV_KEY, ecodes.BTN_TOUCH, 1)
            else:
                vpen.write(ecodes.EV_KEY, ecodes.BTN_TOUCH, 0)
            # Flush
            vpen.syn()
            
    except usb.core.USBError as e:
        if pen_hovering:
            # Need to emit event BTN_TOOL_PEN = 0 when pen is not hovering,
            # just for compliance with the specs.
            # https://www.kernel.org/doc/Documentation/input/event-codes.txt
            vpen.write(ecodes.EV_KEY, ecodes.BTN_TOOL_PEN, 0)
            pen_hovering = False
            vpen.syn()
        if e.args[0] == 19:
            vpen.close()
            raise Exception('Device has been disconnected')
