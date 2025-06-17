import data
import errorcorrectiondata as ecd
import numpy as np
from gf256 import GF256


# x, y: 多項式の係数, yはモニック, x % yを求める
def CalculateRemainder(x, y):
    x = np.array(x)
    y = np.array(y)
    if len(x) < len(y):
        return x
    for i in range(len(x) - len(y) + 1):
        if isinstance(x[0], np.bool):
            x[i : i + len(y)] ^= y & x[i]
        else:
            x[i : i + len(y)] -= y * x[i]
    return x[-len(y) + 1:]


def GenerateErrorCodeBlock(data_code_block, error_code_len):
    data_code_block = [GF256(data_code) for data_code in data_code_block] + [GF256(0)] * error_code_len
    generating_polynomial = ecd.generating_polynomial_coefficient[str(error_code_len)]
    remainder = CalculateRemainder(data_code_block, generating_polynomial)
    return [x.value for x in remainder]



def GenerateErrorCodeBlocks(data_code_blocks, version, error_correction_level):
    total_code_word_num = data.MaxCodeSize(version) // 8
    total_error_block_num = ecd.correction_block_num[error_correction_level][version - 1]
    bigger_block_num = total_code_word_num % total_error_block_num
    smaller_block_num = total_error_block_num - bigger_block_num
    error_code_word_num = ecd.error_words_per_block[error_correction_level][version - 1]
    error_code_blocks = []
    for data_code_block in data_code_blocks:
        error_code_block = GenerateErrorCodeBlock(data_code_block, error_code_word_num)
        error_code_blocks.append(error_code_block)
    return error_code_blocks

if __name__ == "__main__":
    b = [32, 65, 205, 69, 41, 220, 46, 128, 236]
    print(GenerateErrorCodeBlock(b, 17))