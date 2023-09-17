"""
Use the GoDice Python API to integrate GoDice functionality into your own Python applications
"""
__version__ = "0.1.0"

from .factory import (
    create,
    set_shell,
    Shell
)
from .dice import (
    StabilityDescriptor,
    Color,
    Dice
)
