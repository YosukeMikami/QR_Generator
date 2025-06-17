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


def Encode(message):
    segment = Segment(Mode.kKanji)
    for char in message:
        segment.message += char
    code = segment.Encode()
    return code


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