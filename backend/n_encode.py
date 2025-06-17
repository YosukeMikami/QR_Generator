import numpy as np

class Segment:
    def __init__(self, mode, string):
        self.mode = mode

    def BitToList(bit, length):
        return [
            True if (bit >> (length - i - 1)) & 1 == 1\
            else False\
            for i in range(length)
        ]

    def EncodeNumber(string):
        out = []
        # 3文字ごとに分割
        for i in range(0, len(string), 3):
            part = string[i : i + 3]
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


    def EncodeAlphaNum(string):
        def CodeOfAlphaNum(char):
            alpha_num_symbols = {" ": 36, "$": 37, "%": 38, "*": 39, "+": 40, "-": 41, ".": 42, "/": 43, ":": 44}
            if ord("0") <= ord(char) <= ord("9"):
                return ord(char)
            if ord("A") <= ord(char) <= ord("Z"):
                return 10 + ord(char) - ord("A")
            if char in alpha_num_symbols:
                return alpha_num_symbols[char]
            raise ValueError("Input string must contain only numbers, uppercase alphabetical characters, and certain symbols.")

        out = []
        # 2文字ごとに分割
        for i in range(0, len(string), 2):
            part = string[i : i + 2]
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




if __name__ == "__main__":
    print(Segment.EncodeAlphaNum("12345a7"))