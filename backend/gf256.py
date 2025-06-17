from enum import IntEnum, auto


class ValueKind(IntEnum):
    kBit = auto()
    kExp = auto()


class GF256:
    def __init__(self, value):
        assert isinstance(value, int) & 0 <= value < 256
        self.value = value

    def __add__(self, other):
        assert isinstance(other, GF256), "The RHS operand must be a instance of GF256."
        return GF256(self.value ^ other.value)

    def __iadd__(self, other):
        assert isinstance(other, GF256), "The RHS operand must be a instance of GF256."
        self.value ^= other.value
        return self

    def __sub__(self, other):
        assert isinstance(other, GF256), "The RHS operand must be a instance of GF256."
        return self + other

    def __isub__(self, other):
        assert isinstance(other, GF256), "The RHS operand must be a instance of GF256."
        self.value ^= other.value
        return self

    def __mul__(self, other):
        assert isinstance(other, GF256), "The RHS operand must be a instance of GF256."
        mul = 0
        # 多項式として掛け算
        for i in range(8):
            mul ^= (self.value << i) if ((other.value >> i) & 1) == 1 else 0
        generator = 0b100011101 # 生成多項式に対応する元
        # 生成多項式で割る
        for i in range(8, -1, -1):
            shifted_generator = generator << i
            mul = min(mul, mul ^ shifted_generator)
        return GF256(mul)

    def __imul__(self, other):
        assert isinstance(other, GF256), "The RHS operand must be a instance of GF256."
        self.value = (self * other).value
        return self

    def __pow__(self, other):
        assert isinstance(other, int),  "The RHS operand must be a instance of int."
        res = GF256(1)
        for _ in range(other):
            res *= self
        return res

    def __repr__(self):
        return f"GF256({self.value})"

    def __str__(self):
        return f"GF256({self.value})"


if __name__ == "__main__":
    x = GF256(135)
    y = GF256(64)
    print(x * y)