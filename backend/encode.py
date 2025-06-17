import sys

import data
import errorcorrectiondata as ecd
from errorcode import CalculateRemainder
from data import Mode

class Segment:
    def __init__(self, mode=Mode.kEightBitByte):
        self.mode = mode
        self.message = ""

    def Encode(self):
        if self.mode == Mode.kNumber:
            return self.EncodeNumber()
        elif self.mode == Mode.kAlphaNum:
            return self.EncodeAlphaNum()
        elif self.mode == Mode.kEightBitByte:
            return self.Encode8BitByte()
        else:
            return self.EncodeKanji()

    def BitToList(bit, length):
        return [
            True if (bit >> (length - i - 1)) & 1 == 1\
            else False\
            for i in range(length)
        ]

    def EncodeNumber(self):
        out = []
        # 3文字ごとに分割
        for i in range(0, len(self.message), 3):
            part = self.message[i : i + 3]
            try:
                if len(part) == 1:
                        out.extend(Segment.BitToList(int(part), 4))
                elif len(part) == 2:
                    # 2文字を7bitに圧縮
                    out.extend(Segment.BitToList(int(part), 7))
                else:
                    # 3文字を10bitに圧縮
                    out.extend(Segment.BitToList(int(part), 10))
            except ValueError:
                raise ValueError("Input string must contain only numbers.")
        return out


    def EncodeAlphaNum(self):
        def CodeOfAlphaNum(char):
            alpha_num_symbols = {" ": 36, "$": 37, "%": 38, "*": 39, "+": 40, "-": 41, ".": 42, "/": 43, ":": 44}
            if ord("0") <= ord(char) <= ord("9"):
                return int(char)
            if ord("A") <= ord(char) <= ord("Z"):
                return 10 + ord(char) - ord("A")
            if char in alpha_num_symbols:
                return alpha_num_symbols[char]
            raise ValueError("Input string must contain only numbers, uppercase alphabetical characters, and certain symbols.")

        out = []
        # 2文字ごとに分割
        for i in range(0, len(self.message), 2):
            part = self.message[i : i + 2]
            try:
                if len(part) == 1:
                    out.extend(Segment.BitToList(CodeOfAlphaNum(part), 6))
                else:
                    upper_code = CodeOfAlphaNum(part[0])
                    lower_code = CodeOfAlphaNum(part[1])
                    # 2文字を11bitに圧縮
                    out.extend(Segment.BitToList(upper_code * 45 + lower_code, 11))
            except ValueError as e:
                raise e
        return out

    def Encode8BitByte(self):
        def CodeofChar(char):
            code = int(char.encode("cp932").hex(), 16)
            if (code >> 8) == 0:
                return Segment.BitToList(code, 8)
            else:
                return Segment.BitToList(code, 16)

        out = []
        for char in self.message:
            out.extend(CodeofChar(char))
        return out

    def EncodeKanji(self):
        def CodeOfChar(char):
            code = int(char.encode("cp932").hex(), 16)
            if 0x8140 <= code <= 0x9ffc:
                code -= 0x8140
            elif 0xe040 <= code <= 0xebbf:
                code -= 0xc140
            else:
                raise ValueError("Input character must be Kanji")
            upper_byte = (code >> 8) & 0xff
            lower_byte = code & 0xff
            res = upper_byte * 0xc0 + lower_byte
            return Segment.BitToList(res, 13)

        out = []
        for char in self.message:
            out.extend(CodeOfChar(char))
        return out


def ListToBit(list, length):
    word = 0
    for j in range(length):
        word = (word << 1) | (1 if list[j] else 0)
    return word



# def EncodeKanji(char):
#     code = int(char.encode("cp932").hex(), 16)
#     if 0x8140 <= code <= 0x9ffc:
#         code -= 0x8140
#     else:
#         code -= 0xc140
#     upper_byte = (code >> 8) & 0xff
#     lower_byte = code & 0xff
#     res = upper_byte * 0xc0 + lower_byte
#     return BitToList(res, 13)

# this function needs to be refactored.
def Encode(message, error_correction_level):
    segment = Segment(Mode.kKanji)
    for char in message:
        segment.message += char
    code = segment.Encode()
    return code
    # segment = Segment(Mode.kEightBitByte)
    # for char in string:
    #     segment.code.extend(Encode8BitByte(char))
    # version = DecideVersion(4 + data.LenIndicatorLen(1, Mode.kEightBitByte) + len(segment.code), error_correction_level)
    # if version <= 9:
    #     segment.len = len(segment.code) // 8
    #     indicater_len = data.LenIndicatorLen(1, Mode.kEightBitByte)
    #     data_code = BitToList(segment.mode, 4)
    #     data_code.extend(BitToList(segment.len, indicater_len))
    #     data_code.extend(segment.code)
    #     return data_code, version
    # version = DecideVersion(4 + data.LenIndicatorLen(10, Mode.kEightBitByte) + len(segment.code), error_correction_level)
    # if version <= 26:
    #     segment.len = len(segment.code) // 8
    #     indicater_len = data.LenIndicatorLen(10, Mode.kEightBitByte)
    #     data_code = BitToList(segment.mode, 4)
    #     data_code.extend(BitToList(segment.len, indicater_len))
    #     data_code.extend(segment.code)
    #     return data_code, version
    # version = DecideVersion(4 + data.LenIndicatorLen(27, Mode.kEightBitByte) + len(segment.code), error_correction_level)
    # if version <= 40:
    #     segment.len = len(segment.code) // 8
    #     indicater_len = data.LenIndicatorLen(27, Mode.kEightBitByte)
    #     data_code = BitToList(segment.mode, 4)
    #     data_code.extend(BitToList(segment.len, indicater_len))
    #     data_code.extend(segment.code)
    #     return data_code, version
    # print("The input string is too long to encode!")
    # sys.exit(1)


def DivideCodePer8Bit(code):
    code_len = len(code)
    res = []
    for i in range(code_len // 8):
        word = ListToBit(code[i * 8:i * 8 + 8], 8)
        res.append(word)
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
    data_len = len(data_code)
    if data_len % 8 != 0:
        for _ in range(8 - data_len % 8):
            data_code.append(False)
    padding_first = True
    for _ in range(DataCodeWordNum(version, error_correction_level) - len(data_code) // 8):
        if padding_first:
            data_code.extend([True, True, True, False, True, True, False, False])
        else:
            data_code.extend([False, False, False, True, False, False, False, True])
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
    code = []
    if error_correction_level == ecd.Level.kL:
        code.extend([False, True])
    elif error_correction_level == ecd.Level.kM:
        code.extend([False, False])
    elif error_correction_level == ecd.Level.kQ:
        code.extend([True, True])
    else:
        code.extend([True, False])
    code.extend(BitToList(mask_pattern, 3))
    code_shifted = code + [False] * 10
    error_code = CalculateRemainder(code_shifted, [True, False, True, False, False, True, True, False, True, True, True])
    code.extend(error_code)
    res = ListToBit(code, len(code))
    return res ^ 0b101010000010010


def EncodeVersionInfo(version):
    if version <= 6:
        return 0
    code = BitToList(version, 6)
    code_shifted = code + [False] * 12
    error_code = CalculateRemainder(code_shifted, [True, True, True, True, True, False, False, True, False, False, True, False, True])
    code.extend(error_code)
    res = ListToBit(code, code.shape[0])
    return res

if __name__ == "__main__":
    code = Encode("茗", None)
    s = ""
    for i, b in enumerate(code):
        s += "1" if b else "0"
        # if i % 8 == 7:
        #     s += " "
    print(s)