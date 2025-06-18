import math
from enum import IntEnum, auto

import numpy as np

kFinderPatternLen = 7
kFinderPatternSize = kFinderPatternLen ** 2
kAlignmentPatternLen = 5
kAlignmentPatternSize = kAlignmentPatternLen ** 2
kSeparatePatternSize = 45
kFormatInfoSize = 15


class Mode(IntEnum):
    kNumber = 0b0001
    kAlphaNum = 0b0010
    kEightBitByte = 0b0100
    kKanji = 0b1000


class EncodeSize(IntEnum):
    kSmall = auto()
    kMedium = auto()
    kLarge = auto()


def SideLen(version):
    return 4 * (version - 1) + 21


def OverallSize(version):
    return SideLen(version) ** 2


def TimingPatternSize(version):
    if version <= 6:
        alignment_pattern_num = 0
    elif version <= 13:
        alignment_pattern_num = 1
    elif version <= 20:
        alignment_pattern_num = 2
    elif version <= 27:
        alignment_pattern_num = 3
    elif version <= 34:
        alignment_pattern_num = 4
    else:
        alignment_pattern_num = 5
    return (SideLen(version) - 2 * kFinderPatternLen - 2 - 5 * alignment_pattern_num) * 2


def VersionInfoSize(version):
    if version <= 6:
        return 31
    else:
        return 67


def AlignmentPatternLen(version):
    if version == 1:
        return 0
    elif version <= 6:
        return 2
    elif version <= 13:
        return 3
    elif version <= 20:
        return 4
    elif version <= 27:
        return 5
    elif version <= 34:
        return 6
    else:
        return 7


def AlignmentPatternNum(version):
    if version == 1:
        return 0
    return AlignmentPatternLen(version) ** 2 - 3


def FunctionPatternSize(version):
    return kFinderPatternSize * 3 + kSeparatePatternSize + AlignmentPatternNum(version) * kAlignmentPatternSize + TimingPatternSize(version)


def MaxCodeSize(version):
    return OverallSize(version) - FunctionPatternSize(version) - VersionInfoSize(version)


def LenIndicatorLen(encode_size, mode):
    if mode == Mode.kNumber:
        if encode_size == EncodeSize.kSmall:
            return 10
        elif encode_size == EncodeSize.kMedium:
            return 12
        else:
            return 14
    elif mode == Mode.kAlphaNum:
        if encode_size == EncodeSize.kSmall:
            return 9
        elif encode_size == EncodeSize.kMedium:
            return 11
        else:
            return 13
    elif mode == Mode.kEightBitByte:
        if encode_size == EncodeSize.kSmall:
            return 8
        else:
            return 16
    else:
        if encode_size == EncodeSize.kSmall:
            return 8
        elif encode_size == EncodeSize.kMedium:
            return 10
        else:
            return 12


def AlignmentCoordinate(version):
    coordinates = np.array([], dtype=int)
    side_len = SideLen(version)
    current_coordinate = side_len - 7
    last_coordinate = 6
    pattern_len = AlignmentPatternLen(version)
    if version == 32:
        step_size = 26
    else:
        step_size = math.ceil((current_coordinate - last_coordinate) / (pattern_len - 1) / 2) * 2
    while (abs(current_coordinate - last_coordinate) > 10):
        coordinates = np.append(coordinates, [current_coordinate])
        current_coordinate -= step_size
    coordinates = np.append(coordinates, [last_coordinate])
    return np.flipud(coordinates)
