"""
GoDice factory returning a proper Dice based on a shell
"""
import enum
import bleak

from . import dice
from . import xyzinterpret


class Shell(enum.Enum):
    """
    Available shells a dice may be wrapped into
    """
    D6 = 0
    D20 = 1
    D10 = 2
    D10X = 3
    D4 = 4
    D8 = 5
    D12 = 6

xyz_interpret_map = {
    Shell.D6: xyzinterpret.get_rolled_number_d6,
    Shell.D10: xyzinterpret.get_rolled_number_d10,
    Shell.D10X: xyzinterpret.get_rolled_number_d10x,
    Shell.D20: xyzinterpret.get_rolled_number_d20,
    Shell.D4: xyzinterpret.get_rolled_number_d4,
    Shell.D8: xyzinterpret.get_rolled_number_d8,
    Shell.D12: xyzinterpret.get_rolled_number_d12,
}


def create(ble_address: str, dice_shell: Shell, timeout: int=15, disconnect_cb=None):
    """
    Creates Dice API object representing the specified type of a dice
    :param ble_client: BleakClient
    :param dice_shell: Shell
    """
    ble_client = bleak.BleakClient(ble_address, timeout=timeout, disconnected_callback=disconnect_cb)
    _dice = dice.Dice(ble_client)
    set_shell(_dice, dice_shell)
    return _dice


def set_shell(_dice: dice.Dice, dice_shell: Shell):
    """
    Change a dice shell.
    Should be called in order to receive correct number notifications corresponding to a newly set shell
    :param dice: a Dice object to change a shell for
    :param dice_shell: Shell
    """
    _xyzinterpret_fn = xyz_interpret_map[dice_shell]
    _dice._xyz_interpret_fn = _xyzinterpret_fn
