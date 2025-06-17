from enum import IntEnum, auto

import numpy as np


class ValueKind(IntEnum):
    kBit = auto()
    kExp = auto()


class GF2_8:
    def __init__(self, value, kind=ValueKind.kBit):
        if kind == ValueKind.kBit:
            self.value = GF2_8.ConvertBitToExp(value)
        else:
            self.value = value

    def ConvertBitToExp(value):
        if value == 0:
            return 255
        res = 0
        while value != 0b00000001:
            if value & 1 == 1:
                value ^= 0b00011101
                value >>= 1
                value |= 0b10000000
            else:
                value >>= 1
            res += 1
        return res

    def ConvertExpToBit(value):
        if value == 255:
            return 0
        res = 0b00000001
        for _ in range(value):
            if (res >> 7) & 1 == 1:
                res <<= 1
                res ^= 0b00011101
                res &= 0b11111111
            else:
                res <<= 1
        return res

    def __mul__(self, other):
        if self.value == 255 or other.value == 255:
            return GF2_8(255, ValueKind.kExp)
        return GF2_8((self.value + other.value) % 255, ValueKind.kExp)

    def __truediv__(self, other):
        if other.value == 255:
            return None
        if self.value == 255:
            return self
        return GF2_8((self.value - other.value + 255) % 255, ValueKind.kExp)

    def __pow__(self, other):
        return GF2_8((self.value * other) % 255, ValueKind.kExp)

    def __add__(self, other):
        if self.value == 255:
            return other
        if other.value == 255:
            return self
        self_bit = GF2_8.ConvertExpToBit(self.value)
        other_bit = GF2_8.ConvertExpToBit(other.value)
        res_bit = self_bit ^ other_bit
        return GF2_8(res_bit)

    def __sub__(self, other):
        return self + other

    def __iadd__(self, other):
        return self + other

    def __isub__(self, other):
        return self - other

    def __str__(self):
        return f"{self.value}"

    def __repr__(self):
        return f"{self.value}"


def LUDecomposition(A):
    A = A.copy()
    n = A.shape[0]
    U = np.full(A.shape, GF2_8(0))
    L = np.full(A.shape, GF2_8(0))
    for i in range(n):
        L[i, i] = GF2_8(1)
    for i in range(n - 1):
        U[i, i] = A[i, i]
        U[i, i + 1:] = A[i, i + 1:]
        L[i + 1:, i] = A[i + 1:, i] / A[i, i]
        A[i + 1:, i + 1:] -= L[i + 1:, i].reshape([n - i - 1, 1]) @ U[i, i + 1:].reshape([1, n - i - 1])
    U[n - 1, n - 1] = A[n - 1, n - 1]
    return L, U


def Solve(A, b):
    n = A.shape[0]
    L, U = LUDecomposition(A)
    y = np.full([n, ], GF2_8(0))
    y[0] = b[0]
    for i in range(1, n):
        y[i] = (b[i] - np.dot(L[i, :i], y[:i])) / L[i, i]
    x = np.full([n, ], GF2_8(0))
    x[n - 1] = y[n - 1] / U[n - 1, n - 1]
    for i in range(n - 2, -1, -1):
        x[i] = (y[i] - np.dot(U[i, i + 1:], x[i + 1:])) / U[i, i]
    return x
