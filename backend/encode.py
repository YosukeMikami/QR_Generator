import sys

import numpy as np

import bch
import data
import errorcorrectiondata as ecd
from data import Mode


class Segment:
    def __init__(self, mode):
        self.mode = mode
        self.code = np.array([], dtype=bool)
        self.len = 0

    def __repr__(self):
        return f"mode:{self.mode}, len:{self.len},\n{self.code}"


def BitToList(bit, length):
    return np.array([True if (bit >> (length - i - 1)) & 1 == 1 else False for i in range(length)])


def ListToBit(list, length):
    word = 0
    for j in range(length):
        word = (word << 1) | (1 if list[j] else 0)
    return word


def EncodeNumber(string):
    num = int(string)
    if len(string) == 1:
        return BitToList(num, 4)
    if len(string) == 2:
        return BitToList(num, 7)
    return BitToList(num, 10)


alpha_num_symbols = {" ": 36, "$": 37, "%": 38, "*": 39, "+": 40, "-": 41, ".": 42, "/": 43, ":": 44}


def CodeOfAlphaNum(char):
    if ord("0") <= ord(char) <= ord("9"):
        return ord(char)
    if ord("A") <= ord(char) <= ord("Z"):
        return 10 + ord(char) - ord("A")
    return alpha_num_symbols[char]


def EncodeAlphaNum(string):
    if len(string) == 1:
        return BitToList(CodeOfAlphaNum(string), 6)
    else:
        upper_code = CodeOfAlphaNum(string[0])
        lower_code = CodeOfAlphaNum(string[1])
        return BitToList(upper_code * 45 + lower_code, 11)


def Encode8BitByte(char):
    code = int(char.encode("cp932").hex(), 16)
    if (code >> 8) == 0:
        return BitToList(code, 8)
    else:
        return BitToList(code, 16)


def EncodeKanji(char):
    code = int(char.encode("cp932").hex(), 16)
    if 0x8140 <= code <= 0x9ffc:
        code -= 0x8140
    else:
        code -= 0xc140
    upper_byte = (code >> 8) & 0xff
    lower_byte = code & 0xff
    res = upper_byte * 0xc0 + lower_byte
    return BitToList(res, 13)


# def MinModeLen(string):


# this function needs to be refactored.
def Encode(string, error_correction_level):
    segment = Segment(Mode.kEightBitByte)
    for char in string:
        segment.code = np.append(segment.code, Encode8BitByte(char))
    version = DecideVersion(4 + data.LenIndicatorLen(1, Mode.kEightBitByte) + len(segment.code), error_correction_level)
    if version <= 9:
        segment.len = len(segment.code) // 8
        indicater_len = data.LenIndicatorLen(1, Mode.kEightBitByte)
        data_code = np.array(BitToList(segment.mode, 4))
        data_code = np.append(data_code, BitToList(segment.len, indicater_len))
        data_code = np.append(data_code, segment.code)
        return data_code, version
    version = DecideVersion(4 + data.LenIndicatorLen(10, Mode.kEightBitByte) + len(segment.code), error_correction_level)
    if version <= 26:
        segment.len = len(segment.code) // 8
        indicater_len = data.LenIndicatorLen(10, Mode.kEightBitByte)
        data_code = np.array(BitToList(segment.mode, 4))
        data_code = np.append(data_code, BitToList(segment.len, indicater_len))
        data_code = np.append(data_code, segment.code)
        return data_code, version
    version = DecideVersion(4 + data.LenIndicatorLen(27, Mode.kEightBitByte) + len(segment.code), error_correction_level)
    if version <= 40:
        segment.len = len(segment.code) // 8
        indicater_len = data.LenIndicatorLen(27, Mode.kEightBitByte)
        data_code = np.array(BitToList(segment.mode, 4))
        data_code = np.append(data_code, BitToList(segment.len, indicater_len))
        data_code = np.append(data_code, segment.code)
        return data_code, version
    print("The input string is too long to encode!")
    sys.exit(1)


def DivideCodePer8Bit(code):
    code_len = len(code)
    res = np.array([], dtype=int)
    for i in range(code_len // 8):
        word = ListToBit(code[i * 8:i * 8 + 8], 8)
        res = np.append(res, [word])
    return res


def DataCodeWordNum(version, error_correction_level):
    total_code_word_num = data.MaxCodeSize(version) // 8
    total_error_block_num = ecd.correction_block_num[error_correction_level][version - 1]
    bigger_block_num = total_code_word_num % total_error_block_num
    smaller_block_num = total_error_block_num - bigger_block_num
    smaller_total_code_word_num = (total_code_word_num - bigger_block_num) // total_error_block_num
    smaller_data_code_word_num = smaller_total_code_word_num - ecd.error_words_per_block[error_correction_level][version - 1]
    bigger_data_code_word_num = smaller_data_code_word_num + 1
    total_data_code_word_num = smaller_block_num * smaller_data_code_word_num + bigger_block_num * bigger_data_code_word_num
    return total_data_code_word_num


def DecideVersion(data_code_len, error_correction_level):
    version = 1
    data_code_word_num = data_code_len // 8
    while True:
        total_data_code_word_num = DataCodeWordNum(version, error_correction_level)
        if total_data_code_word_num >= data_code_word_num:
            break
        version += 1
        if version > 40:
            break
    return version


def PaddingDataCode(data_code, version, error_correction_level):
    data_len = data_code.shape[0]
    if data_len % 8 != 0:
        for _ in range(8 - data_len % 8):
            data_code = np.append(data_code, [False])
    padding_first = True
    for _ in range(DataCodeWordNum(version, error_correction_level) - data_code.shape[0] // 8):
        if padding_first:
            data_code = np.append(data_code, [True, True, True, False, True, True, False, False])
        else:
            data_code = np.append(data_code, [False, False, False, True, False, False, False, True])
        padding_first = not padding_first
    return data_code


def DivideIntoCodeBlock(data_code_per_8b, version, error_correction_level):
    total_code_word_num = data.MaxCodeSize(version) // 8
    total_error_block_num = ecd.correction_block_num[error_correction_level][version - 1]
    bigger_block_num = total_code_word_num % total_error_block_num
    smaller_block_num = total_error_block_num - bigger_block_num
    smaller_total_code_word_num = (total_code_word_num - bigger_block_num) // total_error_block_num
    smaller_data_code_word_num = smaller_total_code_word_num - ecd.error_words_per_block[error_correction_level][version - 1]
    bigger_data_code_word_num = smaller_data_code_word_num + 1
    data_code_blocks = []
    i = 0
    for _ in range(smaller_block_num):
        data_code_blocks.append(data_code_per_8b[i:i + smaller_data_code_word_num])
        i += smaller_data_code_word_num
    for _ in range(bigger_block_num):
        data_code_blocks.append(data_code_per_8b[i:i + bigger_data_code_word_num])
        i += bigger_data_code_word_num
    return data_code_blocks


def EncodeFormatInfo(error_correction_level, mask_pattern):
    code = np.array([], dtype=bool)
    if error_correction_level == ecd.Level.kL:
        code = np.append(code, [False, True])
    elif error_correction_level == ecd.Level.kM:
        code = np.append(code, [False, False])
    elif error_correction_level == ecd.Level.kQ:
        code = np.append(code, [True, True])
    else:
        code = np.append(code, [True, False])
    code = np.append(code, BitToList(mask_pattern, 3))
    code_shifted = np.append(code, [False for _ in range(10)])
    error_code = bch.CalcRemainder(code_shifted, np.array([True, False, True, False, False, True, True, False, True, True, True]))
    code = np.append(code, [error_code])
    res = ListToBit(code, code.shape[0])
    return res ^ 0b101010000010010


def EncodeVersionInfo(version):
    if version <= 6:
        return 0
    code = BitToList(version, 6)
    code_shifted = np.append(code, [False for _ in range(12)])
    error_code = bch.CalcRemainder(code_shifted, np.array([True, True, True, True, True, False, False, True, False, False, True, False, True]))
    code = np.append(code, [error_code])
    res = ListToBit(code, code.shape[0])
    return res
