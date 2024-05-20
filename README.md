
# GoDice Python API

## Overview

Use the GoDice Python API to integrate GoDice functionality into your own Python applications

[![PyPI version](https://badge.fury.io/py/godice.svg)](https://pypi.org/project/godice)

**Supported features:**

* Turn ON/OFF GoDice RGB LEDs
* Read color (dots color)
* Read battery level
* Get notifications regarding the die state (Rolling or Stable and get the outcome number)
* Use and configure different shells (D6, D20, D12 etc.)

## Installation

```
pip install godice
```

## Demo

Package includes a demo script showing up API features. Command to run it:
```
python -m godice.demo
```

It will discover GoDice devices nearby and connect to a closest one.
Then it setups a dice color and starts listening to dice position changes, outputting a new number each time a dice is flipped.

## Usage

One can import and use the API from any custom Python script like below
```
import asyncio
import bleak
import godice


async def main():
    mac = "00:00:00:00:00:00"
    client = bleak.BleakClient(mac, timeout=15)

    # Python context manager (async with) is used for convenient connection handling
    # Device stays connected during `async with` block execution and auto-disconnected on block finish
    # Otherwise, dice.connect/dice.disconnect can be used instead 
    async with godice.create(client, godice.Shell.D6) as dice:
		print("Connected")
        blue_rgb = (0, 0, 255)
        yellow_rgb = (255, 255, 0)
        off_rgb = (0, 0, 0)
        await dice.set_led(blue_rgb, yellow_rgb)

        color = await dice.get_color()
        battery_lvl = await dice.get_battery_level()
        print(f"Color: {color}")
        print(f"Battery: {battery_lvl}")
        
        print("Listening to position updates. Flip your dice")
        await dice.subscribe_number_notification(notification_callback)
        await asyncio.sleep(30)
        await dice.set_led(off_rgb, off_rgb)


async def notification_callback(number, stability_descr):
    """
    GoDice number notification callback.
    Called each time GoDice is flipped, receiving flip event data:
    :param number: a rolled number
    :param stability_descr: an additional value clarifying device movement state, ie stable, rolling...
    """
    print(f"Number: {number}, stability descriptor: {stability_descr}")


asyncio.run(main())
```
