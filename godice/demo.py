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

    # Python context manager (async with) is used for convenient connection handling
    # Device stays connected during `async with` block execution and auto-disconnected on block finish
    # Otherwise, dice.connect/dice.disconnect can be used instead 
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


def filter_godice_devices(dev_advdata_tuples):
    """
    Receives all discovered devices and returns only GoDice devices
    """
    return [
        (dev, adv_data)
        for dev, adv_data in dev_advdata_tuples
        if dev.name.startswith("GoDice")
    ]


def select_closest_device(dev_advdata_tuples):
    """
    Finds the closest device based on RSSI are returns it
    """
    def _rssi_as_key(dev_advdata):
        _, adv_data = dev_advdata
        return adv_data.rssi

    return max(dev_advdata_tuples, key=_rssi_as_key)


def print_device_info(devices):
    """
    Prints short summary of discovered devices
    """
    for dev, adv_data in devices:
        print(f"Name: {dev.name}, address: {dev.address}, rssi: {adv_data.rssi}")


# identify if the script is called directly and run if so
# asyncio.run starts execution in Python async environment
if __name__ == "__main__":
    asyncio.run(main())
