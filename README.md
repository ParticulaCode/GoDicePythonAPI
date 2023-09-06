
# GoDice Python API

## Overview

Use the GoDice Python API to integrate GoDice functionality into your own Python applications

**Supported features:**

* Turn ON/OFF GoDice RGB LEDs
* Read color (dots color)
* Read battery level
* Get notifications regarding the die state (Rolling or Stable and get the outcome number)
* Use and configure different shells (D6, D20, D12 etc.)

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
    async with godice.create(client, godice.DiceShell.D6) as dice:
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
        await dice.subscribe_number_notification(print_upd)
        await asyncio.sleep(30)
        await dice.set_led(off_rgb, off_rgb)


async def print_upd(stability_descr, number):
    print(f"Stability descriptor: {stability_descr}, number: {number}")


asyncio.run(main())
```
