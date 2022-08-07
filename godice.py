import asyncio
import enum
from sys import maxsize
from bleak import BleakClient
from bleak import BleakScanner
import threading
import queue

# Dice vectors
d6Vectors = {1: (-64, 0, 0),
             2: (0, 0, 64),
             3: (0, 64, 0),
             4: (0, -64, 0),
             5: (0, 0, -64),
             6: (64, 0, 0)}

d20Vectors = {1: [-64, 0, -22],
              2: [42, -42, 40],
              3: [0, 22, -64],
              4: [0, 22, 64],
              5: [-42, -42, 42],
              6: [22, 64, 0],
              7: [-42, -42, -42],
              8: [64, 0, -22],
              9: [-22, 64, 0],
              10: [42, -42, -42],
              11: [-42, 42, 42],
              12: [22, -64, 0],
              13: [-64, 0, 22],
              14: [42, 42, 42],
              15: [-22, -64, 0],
              16: [42, 42, -42],
              17: [0, -22, -64],
              18: [0, -22, 64],
              19: [-42, 42, -42],
              20: [64, 0, 22]}

d24Vectors = {1: [20, -60, -20],
              2: [20, 0, 60],
              3: [-40, -40, 40],
              4: [-60, 0, 20],
              5: [40, 20, 40],
              6: [-20, -60, -20],
              7: [20, 60, 20],
              8: [-40, 20, -40],
              9: [-40, 40, 40],
              10: [-20, 0, 60],
              11: [-20, -60, 20],
              12: [60, 0, 20],
              13: [-60, 0, -20],
              14: [20, 60, -20],
              15: [20, 0, -60],
              16: [40, -20, -40],
              17: [-20, 60, -20],
              18: [-40, -40, -40],
              19: [40, -20, 40],
              20: [20, -60, 20],
              21: [60, 0, -20],
              22: [40, 20, -40],
              23: [-20, 0, -60],
              24: [-20, 60, 20]}

# D20 Transforms
d10Transform = {1: 8,
                2: 2,
                3: 6,
                4: 1,
                5: 4,
                6: 3,
                7: 9,
                8: 0,
                9: 7,
                10: 5,
                11: 5,
                12: 7,
                13: 0,
                14: 9,
                15: 3,
                16: 4,
                17: 1,
                18: 6,
                19: 2,
                20: 8,
                }

d10XTransform = {1: 80,
                 2: 20,
                 3: 60,
                 4: 10,
                 5: 40,
                 6: 30,
                 7: 90,
                 8: 0,
                 9: 70,
                 10: 50,
                 11: 50,
                 12: 70,
                 13: 0,
                 14: 90,
                 15: 30,
                 16: 40,
                 17: 10,
                 18: 60,
                 19: 20,
                 20: 80,
                 }

# D24 Transforms
d4Transform = {1: 3,
               2: 1,
               3: 4,
               4: 1,
               5: 4,
               6: 4,
               7: 1,
               8: 4,
               9: 2,
               10: 3,
               11: 1,
               12: 1,
               13: 1,
               14: 4,
               15: 2,
               16: 3,
               17: 3,
               18: 2,
               19: 2,
               20: 2,
               21: 4,
               22: 1,
               23: 3,
               24: 2
               }

d8Transform = {
    1: 3,
    2: 3,
    3: 6,
    4: 1,
    5: 2,
    6: 8,
    7: 1,
    8: 1,
    9: 4,
    10: 7,
    11: 5,
    12: 5,
    13: 4,
    14: 4,
    15: 2,
    16: 5,
    17: 7,
    18: 7,
    19: 8,
    20: 2,
    21: 8,
    22: 3,
    23: 6,
    24: 6
}

d12Transform = {
    1: 1,
    2: 2,
    3: 3,
    4: 4,
    5: 5,
    6: 6,
    7: 7,
    8: 8,
    9: 9,
    10: 10,
    11: 11,
    12: 12,
    13: 1,
    14: 2,
    15: 3,
    16: 4,
    17: 5,
    18: 6,
    19: 7,
    20: 8,
    21: 9,
    22: 10,
    23: 11,
    24: 12
}

class DieType(enum.Enum):
    D6 = 0
    D20 = 1
    D10 = 2
    D10x = 3
    D4 = 4
    D8 = 5
    D12 = 6


# Main GoDice object class
class GoDice:
    def __init__(self, result_queue: queue.Queue, device):
        self.client: BleakClient = None  # Stores client in die loop
        self.device = device             # Bluetooth device to connect to
        self.initiated = False           # Is the die fully initiated
        self.primary_service = None      # Die's primary uart service
        self.recv_characteristic = None  # The reception characteristic
        self.send_characteristic = None  # The sending characteristic
        self.result_queue = result_queue    # The queue of messages received by the die
        self.to_send_queue = queue.Queue()  # The queue of messages to send to the die
        self.loop = None                # The asyncio loop of die thread

        """
        0 -> D6 (default)
        1 -> D20
        2 -> D10
        3 -> D10x
        4 -> D4
        5 -> D8
        6 -> D12
        """
        self.die_type = 0
        self.rolled_value = 0

    def init_die(self):
        """
        Starts the die loop coroutine
        """
        asyncio.run(self._die_loop())

    async def _die_loop(self):
        """
        Main loop of die object, connects to given device and processes messages sent by the die
        """
        # TODO: Add support for disconnecting (Manually and in case of sudden disconnect)
        async with BleakClient(self.device) as self.client:

            print(f"\nConnected to {self.client.address}")

            svcs = await self.client.get_services()
            for service in svcs:
                if service.uuid == "6e400001-b5a3-f393-e0a9-e50e24dcca9e":
                    self.primary_service = service

            self.recv_characteristic = self.primary_service.get_characteristic("6e400003-b5a3-f393-e0a9-e50e24dcca9e")
            self.send_characteristic = self.primary_service.get_characteristic("6e400002-b5a3-f393-e0a9-e50e24dcca9e")

            await self.client.start_notify(self.recv_characteristic, self._handle_notification_change)
            self.initiated = True

            self.loop = asyncio.get_running_loop()
            while True:
                # Waiting until we get a new message to send to the die
                data = await self.loop.run_in_executor(None, self._queue_get_wrapper)
                if data is not None:
                    # Sending waiting message to the die
                    await self.client.write_gatt_char(self.send_characteristic, data)

    def _queue_get_wrapper(self):
        """
        Wrapper method for a blocking get request
        """
        return self.to_send_queue.get(block=True)

    def send_battery_request(self):
        """
        Sends request for battery level
        """
        self.to_send_queue.put((3).to_bytes(1, byteorder="big"))

    def send_color_request(self):
        """
        Sends request for color of die
        """
        self.to_send_queue.put((23).to_bytes(1, byteorder="big"))

    def set_led(self, led1: list, led2: list):
        """
        Turn On/Off RGB LEDs, will turn off if led1 and led2 are None
        :param led1: a list to control the 1st LED in the following format '[R, G, B]'
                     where R, G, and B are numbers in the range of 0-255
        :param led2: a list to control the 2nd LED in the following format '[R, G, B]'
                     where R, G, and B are numbers in the range of 0-255
        """

        # Setting LEDs to [0, 0, 0] if given None
        adjust_1 = led1 if led1 is not None else [0, 0, 0]
        adjust_2 = led2 if led2 is not None else [0, 0, 0]

        # Making sure the length is accurate
        if len(adjust_1) == 3 and len(adjust_2) == 3:
            # Making sure all values are in correct range
            for i in range(3):
                adjust_1[i] = max(min(adjust_1[i], 255), 0)
                adjust_2[i] = max(min(adjust_2[i], 255), 0)

            msg = bytearray()

            # LED message identifier
            msg.append(8)
            # Appending the LED values to the message
            for value in adjust_1:
                msg.append(value)
            for value in adjust_2:
                msg.append(value)

            self.to_send_queue.put(msg)

    def pulse_led(self, pulse_count, on_time, off_time, rgb):
        """
        Pulses the die's leds for set time
        :param pulse_count: How many pulses
        :param on_time: How much time to spend on (units of 10 ms)
        :param off_time: How much time to spend off (units of 10 ms)
        :param rgb: List of RGB values to set die to pulse to
        """
        if len(rgb) == 3:
            adj_rgb = []
            for i in range(3):
                adj_rgb.append(max(min(rgb[i], 255), 0))

            msg = bytearray()

            # LED pulse message identifier
            msg.append(16)
            # Appending message modifiers to the message
            msg.append(pulse_count)
            msg.append(on_time)
            msg.append(off_time)
            for color in adj_rgb:
                msg.append(color)
            msg.append(1)
            msg.append(0)

            self.to_send_queue.put(msg)

    def _wait_for_msg(self):
        while self.to_send_queue.empty():
            pass
        return self.to_send_queue.get()

    def _handle_notification_change(self, handle, data: bytearray):
        """
        Callback function when die sends value, processes the data sent by die
        """
        first_byte = data[0]
        if first_byte == 82:
            # Die is in rolling mode
            self.result_queue.put("R")
        else:
            second_byte = data[1]
            third_byte = data[2]

            if first_byte == 66 and second_byte == 97 and third_byte == 116:
                # Battery level
                self.result_queue.put(("B", data[3]))

            elif first_byte == 67 and second_byte == 111 and third_byte == 108:
                # Color
                self.result_queue.put(("C", data[3]))

            elif first_byte == 83:
                # Stable
                xyz = _get_xyz_from_bytes(data, 1)
                self.rolled_value = self._get_rolled_number(xyz)
                self.result_queue.put(("S", self.rolled_value))

            elif second_byte == 83:
                # Other stable events
                xyz = _get_xyz_from_bytes(data, 2)
                self.rolled_value = self._get_rolled_number(xyz)

                if first_byte == 70:
                    # Fake stable
                    self.result_queue.put(("FS", self.rolled_value))

                elif first_byte == 84:
                    # Tilt stable
                    self.result_queue.put(("TS", self.rolled_value))

                elif first_byte == 77:
                    # Move stable
                    self.result_queue.put(("MS", self.rolled_value))

    def _get_rolled_number(self, xyz):
        """
        Gets xyz position of die and returns it's rolled value
        :param xyz: xyz position of die
        :return: the die's rolled value
        """
        value = 0
        if self.die_type == 0:
            value = _get_closest_vector(d6Vectors, xyz)
        elif 0 < self.die_type <= 3:
            value = _get_closest_vector(d20Vectors, xyz)
        elif 3 < self.die_type <= 6:
            value = _get_closest_vector(d24Vectors, xyz)

        # Not D6 Or D20:
        if not (self.die_type == 0 or self.die_type == 1):

            if self.die_type == 2:
                value = d10Transform[value]
            elif self.die_type == 3:
                value = d10XTransform[value]
            elif self.die_type == 4:
                value = d4Transform[value]
            elif self.die_type == 5:
                value = d8Transform[value]
            elif self.die_type == 6:
                value = d12Transform[value]

        return value

    def set_die_type(self, new_die_type):
        """
        :param new_die_type: DieType (Enum)
                D6 = 0
                D20 = 1
                D10 = 2
                D10x = 3
                D4 = 4
                D8 = 5
                D12 = 6
        :return: changes die type to new die type
        """
        self.die_type = new_die_type.value



# ============ Utility methods ==============

def _get_xyz_from_bytes(data, start_byte):
    """
    :param data: raw data sent by die
    :param start_byte: the byte in which the xyz coordinates start at
    :return: a tuple of the xyz coordinates sent by the die
    """
    x = int.from_bytes(data[start_byte].to_bytes(1, byteorder="big"), signed=True, byteorder="big")
    y = int.from_bytes(data[start_byte + 1].to_bytes(1, byteorder="big"), signed=True, byteorder="big")
    z = int.from_bytes(data[start_byte + 2].to_bytes(1, byteorder="big"), signed=True, byteorder="big")
    return x, y, z


def _get_closest_vector(die_table, coord):
    """
    :param die_table: die vector table to check for
    :param coord: die's xyz coordinates
    :return: the value of the closest vector to the die's vector
    """
    coord_x = coord[0]
    coord_y = coord[1]
    coord_z = coord[2]

    min_distance = maxsize
    value = 0

    # Calculating distance to each value in vector array
    for die_value in die_table:
        vector = die_table[die_value]
        x_result = coord_x - vector[0]
        y_result = coord_y - vector[1]
        z_result = coord_z - vector[2]

        cur_dist = ((x_result ** 2) + (y_result ** 2) + (z_result ** 2))
        if cur_dist < min_distance:
            min_distance = cur_dist
            value = die_value

    return value


def create_dice(device):
    """
    Creates die object and start a new thread for it
    :param device: Bluetooth device of die
    :return: New die object
    """
    die = GoDice(queue.Queue(), device)
    threading.Thread(target=die.init_die, daemon=True).start()
    return die


# Method to discover dice bluetooth devices
async def _discover_dice_async():
    """
    Used to discover nearby charged GoDice
    Returns an array of GoDice
    """
    # Discovering local devices using BLE
    devices = await BleakScanner.discover(timeout=7)

    dice_devices = []

    # Iterating through found devices
    for d in devices:
        if isinstance(d.name, str):
            # Filtering only GoDice
            if d.name.startswith("GoDice"):
                dice_devices.append(d)
    return dice_devices


def discover_dice():
    """
    Used to discover nearby charged GoDice
    Returns an array of GoDice
    """
    return asyncio.run(_discover_dice_async())
