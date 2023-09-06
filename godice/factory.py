"""
GoDice factory returning a proper Dice based on a shell
"""
import enum
import bleak

from . import dice
from . import xyzinterpret


class DiceShell(enum.Enum):
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
    DiceShell.D6: xyzinterpret.get_rolled_number_d6,
    DiceShell.D10: xyzinterpret.get_rolled_number_d10,
    DiceShell.D10X: xyzinterpret.get_rolled_number_d10x,
    DiceShell.D20: xyzinterpret.get_rolled_number_d20,
    DiceShell.D4: xyzinterpret.get_rolled_number_d4,
    DiceShell.D8: xyzinterpret.get_rolled_number_d8,
    DiceShell.D12: xyzinterpret.get_rolled_number_d12,
}


def create(ble_client: bleak.BleakClient, dice_shell: DiceShell):
    """
    Creates Dice API object representing the specified type of a dice
    :param ble_client: BleakClient
    :param dice_shell: DiceShell
    """
    _dice = dice.Dice(ble_client)
    set_shell(_dice, dice_shell)
    return _dice


def set_shell(_dice: dice.Dice, dice_shell: DiceShell):
    """
    Change a dice shell.
    Should be called in order to receive correct number notifications corresponding to a newly set shell
    :param dice: a Dice object to change a shell for
    :param dice_shell: DiceShell
    """
    _xyzinterpret_fn = xyz_interpret_map[dice_shell]
    _dice._xyz_interpret_fn = _xyzinterpret_fn
