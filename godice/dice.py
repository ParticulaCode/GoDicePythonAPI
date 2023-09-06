"""
Dice API
"""
import asyncio
import struct
import enum
from typing import Callable, Awaitable

class Color(enum.Enum):
    """
    Color of a dice (dots)
    """
    BLACK = 0
    RED = 1
    GREEN = 2
    BLUE = 3
    YELLOW = 4
    ORANGE = 5


class StabilityDescriptor(enum.Enum):
    """
    Value describing a movement state taking place at the time of position capture
    """
    ROLLING = 1
    STABLE = 2
    TILT_STABLE = 3
    FAKE_STABLE = 4
    MOVE_STABLE = 5


class Dice:
    """
    Represents a dice providing API to features
    """
    def __init__(self, ble_client) -> None:
        self._client = ble_client
        self._rx_char = None
        self._tx_char = None
        self._color = None
        self._color_upd_q = asyncio.Queue()
        self._battery_lvl_upd_q = asyncio.Queue()
        self._xyz_interpret_fn = None
        self._nop_cb = lambda _: None
        self._position_upd_cb = self._nop_cb

    async def connect(self):
        await self._client.connect()
        self._tx_char = self._client.services.get_characteristic(
            "6e400002-b5a3-f393-e0a9-e50e24dcca9e"
        )
        self._rx_char = self._client.services.get_characteristic(
            "6e400003-b5a3-f393-e0a9-e50e24dcca9e"
        )
        await self._client.start_notify(self._rx_char, self._handle_upd)

    async def disconnect(self):
        await self._client.disconnect()

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()

    async def set_led(self, led1_rgb_tuple, led2_rgb_tuple):
        """
        Set LED color
        :param led1_rgb_tuple: RGB tuple for LED 1
        :param led2_rgb_tuple: RGB tuple for LED 2
        """
        _validate_rgb_tuple(led1_rgb_tuple)
        _validate_rgb_tuple(led2_rgb_tuple)

        cmd_code = 8
        data = bytearray([cmd_code, *led1_rgb_tuple, *led2_rgb_tuple])
        await self._client.write_gatt_char(self._tx_char, data)

    async def pulse_led(self, pulse_count, on_time_ms, off_time_ms, rgb_tuple):
        """
        Pulses the die's leds for set time
        :param pulse_count: How many pulses
        :param on_time_ms: How much time to spend on (units of 10 ms)
        :param off_time_ms: How much time to spend off (units of 10 ms)
        :param rgb_tuple: tuple of RGB values set to pulse
        """
        _validate_rgb_tuple(rgb_tuple)

        cmd_code = 16
        cmd_ending = [1, 0]
        data = bytearray(
            [cmd_code, pulse_count, on_time_ms, off_time_ms, *rgb_tuple, *cmd_ending]
        )
        await self._client.write_gatt_char(self._tx_char, data)

    async def get_color(self):
        """
        Read dice color
        """
        self._color = self._color or await self._fetch_color()
        return self._color

    async def _fetch_color(self):
        cmd_code = 23
        msg = bytearray([cmd_code])
        await self._client.write_gatt_char(self._tx_char, msg)
        color = await self._color_upd_q.get()
        return color

    async def get_battery_level(self):
        """
        Read a battery level
        """
        cmd_code = 3
        msg = bytearray([cmd_code])
        await self._client.write_gatt_char(self._tx_char, msg)
        return await self._battery_lvl_upd_q.get()

    async def subscribe_number_notification(self, callback: Callable[[int, StabilityDescriptor], Awaitable[None]]):
        """
        Subscribe to receiving position change notifications
        :param callback: callback function receiving number update notifications
        """
        self._position_upd_cb = callback

    async def _handle_upd(self, _char, data: bytearray):
        first_byte = data[0]
        if first_byte == 82:
            await self._position_upd_cb(0, StabilityDescriptor.ROLLING)
            return

        second_byte = data[1]
        third_byte = data[2]
        if first_byte == 66 and second_byte == 97 and third_byte == 116:
            await self._battery_lvl_upd_q.put(data[3])
            return

        if first_byte == 67 and second_byte == 111 and third_byte == 108:
            await self._color_upd_q.put(Color(data[3]))
            return

        if first_byte == 83:
            xyz = _get_xyz_from_bytes(data[1:4])
            rolled_value = self._xyz_interpret_fn(xyz)
            await self._position_upd_cb(rolled_value, StabilityDescriptor.STABLE)
            return

        if second_byte == 83:
            xyz = _get_xyz_from_bytes(data[2:5])
            rolled_value = self._xyz_interpret_fn(xyz)
            descr = None
            if first_byte == 70:
                descr = StabilityDescriptor.FAKE_STABLE
            elif first_byte == 84:
                descr = StabilityDescriptor.TILT_STABLE
            elif first_byte == 77:
                descr = StabilityDescriptor.MOVE_STABLE
            else:
                descr = None
            await self._position_upd_cb(rolled_value, descr)


def _validate_rgb_tuple(rgb_tuple):
    def is_any_out_of_range():
        rgb_range = range(256)
        return any(code not in rgb_range for code in rgb_tuple)

    if len(rgb_tuple) != 3 or is_any_out_of_range():
        raise ValueError(
            f"rgb_tuple is expected to be a 3 numbers tuple, got {rgb_tuple}"
        )


def _get_xyz_from_bytes(xyz_bytes):
    return struct.unpack(">bbb", xyz_bytes)
