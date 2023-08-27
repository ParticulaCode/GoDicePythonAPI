
# GoDice Python API

## Overview

Use the GoDice Python API to integrate GoDice functionality into your own Python applications

**Supported features:**

* Turn ON/OFF GoDice RGB LEDs
* Read color (dots color)
* Read battery level
* Get notifications regarding the die state (Rolling or Stable and get the outcome number)
* Use and configure different shells (D6, D20, D12 etc.)


## Usage

```
import asyncio
import bleak
import godice


async def print_upd(stability_descr, number):
    print(f"Stability descriptor: {stability_descr}, number: {number}")


def filter_godice_devices(devices):
    return [
        dev for dev in devices if dev.name.startswith("GoDice")
    ]


async def main():
    print("Discovering GoDice devices...")
    devices = await bleak.BleakScanner.discover(timeout=10)
    devices = filter_godice_devices(devices)

    print("Connecting to a dice...")
    dev = devices[0]
    client = bleak.BleakClient(dev, timeout=15)
    
    async with godice.create(client, godice.DiceType.D6) as dice:
        print("Connected")

        blue_rgb = (0, 0, 255)
        yellow_rgb = (255, 255, 0)
        off_rgb = (0, 0, 0)
        await dice.set_led(blue_rgb, yellow_rgb)

        color = await dice.get_color()
        battery_lvl = await dice.get_battery_level()
        print(f"Color: {color}")
        print(f"Battery: {battery_lvl}")
        
        print("Listening to dice position updates. Flip your dice")
        await dice.subscribe_number_notification(print_upd)
        await asyncio.sleep(30)
        await dice.set_led(off_rgb, off_rgb)


asyncio.run(main())
```

## Installation

- once deployed to PyPI

```
pip install godice
```

- meanwhile, to install a local copy
1. Clone the repo
2. cd into the root dir
3. Install a local copy
```
pip install .
```
