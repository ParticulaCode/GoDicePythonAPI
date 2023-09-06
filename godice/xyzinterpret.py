"""
Tools needed to translate coords sent by a dice to a resulting number based on a dice type
"""

import math

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

def _get_closest_vector(die_table, coord):
    """
    Calculates distance to each number value of a dice

    :param die_table: die vector table to check for
    :param coord: die's xyz coordinates
    :return: the value of the closest vector to the die's vector
    """

    def _distance_as_key(key):
        vec = die_table[key]
        return math.dist(coord, vec)
    return min(die_table.keys(), key=_distance_as_key)


def get_rolled_number_d6(xyz):
    return _get_closest_vector(d6Vectors, xyz)

def get_rolled_number_d20(xyz):
    return _get_closest_vector(d20Vectors, xyz)

def get_rolled_number_d10(xyz):
    value = get_rolled_number_d20(xyz)
    return d10Transform[value]

def get_rolled_number_d10x(xyz):
    value = get_rolled_number_d20(xyz)
    return d10XTransform[value]

def get_rolled_number_d4(xyz):
    value = _get_closest_vector(d24Vectors, xyz)
    return d4Transform[value]

def get_rolled_number_d8(xyz):
    value = _get_closest_vector(d24Vectors, xyz)
    return d8Transform[value]

def get_rolled_number_d12(xyz):
    value = _get_closest_vector(d24Vectors, xyz)
    return d12Transform[value]
