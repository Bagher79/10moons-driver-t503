# 10moons-driver-t503

Simple driver for 10moons T503 tablet for linux

## About

Driver which provides basic functionality for 10moons T503 tablet:
* Correct X and Y positioning
* Pressure sensitivity

This tablet has 4096 levels in both axes and 2047 levels of pressure.

## How to use

Clone or download this repository.

```
git clone https://github.com/jgobi/10moons-driver-t503.git
```

Then install all dependencies listed in _requirements.txt_ file either using python virtual environments or not.

```
python -m pip install -r requirements.txt
```

Connect tablet to your computer and then run _driver.py_ file with sudo privileges.

```
sudo python driver.py
```

**You need to connect your tablet and run the driver prior to launching a drawing software otherwise the device will not be recognized by it.**

## Configuring tablet

Configuration of the driver placed in _config.yaml_ file.

You may need to change the *vendor_id* and the *product_id* but I'm not sure (You device can have the same values as mine, but if it is not you can run the *lsusb* command to find yours).

## Credits

Some parts of code are taken from: https://github.com/Mantaseus/Huion_Kamvas_Linux

I forked this repository from https://github.com/alex-s-v/10moons-driver.git, and then I fixed some bugs and removed the features that doesn't work in my tablet and I didn't need (and so didn't waste time searching about).

I spent too much time searching about and trying to fix these bugs, and this webpage was the most helpful for me, maybe it helps you too someday: https://www.kernel.org/doc/Documentation/input/event-codes.txt

## Known issues

- No button works;
- When the bottom button of the pen is pressed, the driver crashes and you need to reconnect the tablet in the USB and then restart the driver.