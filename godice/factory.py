"""
A factory for all dice types
"""
import enum
import bleak

from . import dice
from . import xyzinterpret


class DiceType(enum.Enum):
    """
    Available types of a dice (shells)
    """
    D6 = 0
    D20 = 1
    D10 = 2
    D10X = 3
    D4 = 4
    D8 = 5
    D12 = 6

xyz_interpret_map = {
    DiceType.D6: xyzinterpret.get_rolled_number_d6,
    DiceType.D10: xyzinterpret.get_rolled_number_d10,
    DiceType.D10X: xyzinterpret.get_rolled_number_d10x,
    DiceType.D20: xyzinterpret.get_rolled_number_d20,
    DiceType.D4: xyzinterpret.get_rolled_number_d4,
    DiceType.D8: xyzinterpret.get_rolled_number_d8,
    DiceType.D12: xyzinterpret.get_rolled_number_d12,
}


def create(ble_client: bleak.BleakClient, dice_type: DiceType):
    """
    Creates an object representing the specified dice type
    """
    _xyzinterpret_fn = xyz_interpret_map[dice_type]
    return dice.Dice(ble_client, _xyzinterpret_fn)
