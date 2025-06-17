import data
import errorcorrectiondata as ecd
import numpy as np
from gf2_8 import GF2_8, Solve, ValueKind


def CalcDataCodePolynomial(coefficient, error_code_len, x):
    data_len = len(coefficient)
    terms = np.array([x ** (data_len + error_code_len - i - 1) for i in range(data_len)])
    return np.dot(np.array([GF2_8(i) for i in coefficient]), terms)


def GenerateRHS(coefficient, error_code_len):
    rhs = np.array([])
    for i in range(error_code_len):
        rhs = np.append(rhs, [CalcDataCodePolynomial(coefficient, error_code_len, GF2_8(i, ValueKind.kExp))])
    return rhs


def GenerateLHS(error_code_len):
    return np.array([[GF2_8((i * j) % 255, ValueKind.kExp) for i in range(error_code_len - 1, -1, -1)] for j in range(0, error_code_len)])


def GenerateErrorCodeBlock(data_code_block, error_code_len):
    A = GenerateLHS(error_code_len)
    b = GenerateRHS(data_code_block, error_code_len)
    x = Solve(A, b)
    return np.array([GF2_8.ConvertExpToBit(i.value) for i in x])


def GenerateErrorCodeBlocks(data_code_blocks, version, error_correction_level):
    total_code_word_num = data.MaxCodeSize(version) // 8
    total_error_block_num = ecd.correction_block_num[error_correction_level][version - 1]
    bigger_block_num = total_code_word_num % total_error_block_num
    smaller_block_num = total_error_block_num - bigger_block_num
    error_code_word_num = ecd.error_words_per_block[error_correction_level][version - 1]
    error_code_blocks = []
    i = 0
    for j in range(smaller_block_num + bigger_block_num):
        error_code_block = GenerateErrorCodeBlock(data_code_blocks[i], error_code_word_num)
        error_code_blocks.append(error_code_block)
        i += 1
    return error_code_blocks
