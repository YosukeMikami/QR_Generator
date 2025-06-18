import errorcorrectiondata as ecd
from errorcode import CalculateRemainder
from data import Mode, EncodeSize, LenIndicatorLen

class Segment:
    def __init__(self, mode=Mode.kEightBitByte, encode_size=EncodeSize.kSmall):
        self.mode = mode
        self.message = ""
        self.encode_size = encode_size

    def Encode(self):
        if self.mode == Mode.kNumber:
            self.data_code = self.EncodeNumber()
        elif self.mode == Mode.kAlphaNum:
            self.data_code = self.EncodeAlphaNum()
        elif self.mode == Mode.kEightBitByte:
            self.data_code = self.Encode8BitByte()
        else:
            self.data_code = self.EncodeKanji()
        header = self.EncodeHeader()
        return header + self.data_code

    def BitToList(bit, length):
        return [
            True if (bit >> (length - i - 1)) & 1 == 1\
            else False\
            for i in range(length)
        ]

    def EncodeHeader(self):
        indicator_len = LenIndicatorLen(self.encode_size, self.mode)
        header = Segment.BitToList(self.mode, 4)
        char_num = len(self.data_code) // 8 if self.mode == Mode.kEightBitByte else len(self.message)
        header.extend(Segment.BitToList(char_num, indicator_len))
        return header

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

def IsExclusiveNumber(char):
    return char in "0123456789"

def IsExclusiveAlphaNum(char):
    return char in " $%*+-./:" or ord("A") <= ord(char) <= ord("Z")

def IsExclusiveKanji(char):
    code = int(char.encode("cp932").hex(), 16)
    return not ((code >> 8) == 0)

def ExclusiveTypeOf(char):
    return Mode.kNumber if IsExclusiveNumber(char)\
           else Mode.kAlphaNum if IsExclusiveAlphaNum(char)\
           else Mode.kKanji if IsExclusiveKanji(char)\
           else Mode.kEightBitByte

def Encode(message):
    code = []
    segment = Segment(ExclusiveTypeOf(message[0]), EncodeSize.kSmall)
    segment.message += message[0]
    for char in message[1:]:
        char_type = ExclusiveTypeOf(char)
        if segment.mode == char_type:
            segment.message += char
        else:
            code.extend(segment.Encode())
            segment = Segment(char_type, EncodeSize.kSmall)
            segment.message += char
    code.extend(segment.Encode())
    return code


def EncodeFormatInfo(error_correction_level, mask_pattern):
    def ListToBit(l):
        res = 0
        for i, v in enumerate(l):
            res += int(v) << (len(l) - 1 - i)
        return res

    code = []
    if error_correction_level == ecd.Level.kL:
        code.extend([False, True])
    elif error_correction_level == ecd.Level.kM:
        code.extend([False, False])
    elif error_correction_level == ecd.Level.kQ:
        code.extend([True, True])
    else:
        code.extend([True, False])
    code.extend(Segment.BitToList(mask_pattern, 3))
    code_shifted = code + [False] * 10
    error_code = CalculateRemainder(code_shifted, [True, False, True, False, False, True, True, False, True, True, True])
    code.extend(error_code)
    res = ListToBit(code)
    return res ^ 0b101010000010010


def EncodeVersionInfo(version):
    def ListToBit(l):
        res = 0
        for i, v in enumerate(l):
            res += int(v) << (len(l) - 1 - i)
        return res

    if version <= 6:
        return 0
    code = Segment.BitToList(version, 6)
    code_shifted = code + [False] * 12
    error_code = CalculateRemainder(code_shifted, [True, True, True, True, True, False, False, True, False, False, True, False, True])
    code.extend(error_code)
    res = ListToBit(code)
    print(res)
    return res

if __name__ == "__main__":
    print(ExclusiveTypeOf("あ"))