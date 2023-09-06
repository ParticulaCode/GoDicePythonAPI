"""
Demo script that connects to the closest dice, sets LED color and listens for position updates
"""
import asyncio
import bleak
import godice


async def main():
    print("Discovering GoDice devices...")
    discovery_res = await bleak.BleakScanner.discover(timeout=10, return_adv=True)
    dev_advdata_tuples = discovery_res.values()
    dev_advdata_tuples = filter_godice_devices(dev_advdata_tuples)

    print("Discovered devices...")
    print_device_info(dev_advdata_tuples)

    print("Connecting to a closest device...")
    dev, _adv_data = select_closest_device(dev_advdata_tuples)
    client = bleak.BleakClient(dev, timeout=15)

    async with godice.create(client, godice.DiceShell.D6) as dice:
        print(f"Connected to {dev.name}")

        blue_rgb = (0, 0, 255)
        yellow_rgb = (255, 255, 0)
        off_rgb = (0, 0, 0)
        await dice.set_led(blue_rgb, yellow_rgb)

        color = await dice.get_color()
        battery_lvl = await dice.get_battery_level()
        print(f"Color: {color}")
        print(f"Battery: {battery_lvl}")

        print("Listening to position updates. Flip your dice")
        await dice.subscribe_number_notification(print_notification)
        await asyncio.sleep(30)
        await dice.set_led(off_rgb, off_rgb)


async def print_notification(number, stability_descr):
    print(f"Number: {number}, stability descriptor: {stability_descr}")


def filter_godice_devices(dev_advdata_tuples):
    return [
        (dev, adv_data)
        for dev, adv_data in dev_advdata_tuples
        if dev.name.startswith("GoDice")
    ]


def select_closest_device(dev_advdata_tuples):
    def _rssi_as_key(dev_advdata):
        _, adv_data = dev_advdata
        return adv_data.rssi

    return max(dev_advdata_tuples, key=_rssi_as_key)


def print_device_info(devices):
    for dev, adv_data in devices:
        print(f"Name: {dev.name}, address: {dev.address}, rssi: {adv_data.rssi}")


if __name__ == "__main__":
    asyncio.run(main())
