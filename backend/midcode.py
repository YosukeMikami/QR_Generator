import errorcorrectiondata as ecd
import data

class LengthError(Exception):
    pass

def BlockInfo(version, error_correction_level):
    total_code_word_capacity = data.MaxCodeSize(version) // 8
    total_error_block_capacity = ecd.correction_block_num[error_correction_level][version - 1]
    bigger_block_capacity = total_code_word_capacity % total_error_block_capacity
    smaller_block_capacity = total_error_block_capacity - bigger_block_capacity
    smaller_total_code_word_capacity =\
        (total_code_word_capacity - bigger_block_capacity) // total_error_block_capacity
    smaller_data_code_word_capacity =\
        smaller_total_code_word_capacity \
        - ecd.error_words_per_block[error_correction_level][version-1]
    bigger_data_code_word_capacity =\
        smaller_data_code_word_capacity + 1
    return (smaller_block_capacity, smaller_data_code_word_capacity), \
           (bigger_block_capacity, bigger_data_code_word_capacity)

def DataCodeWordCapacity(version, error_correction_level):
    (smaller_block_capacity, smaller_data_code_word_capacity),\
    (bigger_block_capacity, bigger_data_code_word_capacity) =\
        BlockInfo(version, error_correction_level)
    data_code_word_capacity =\
        smaller_block_capacity * smaller_data_code_word_capacity\
        + bigger_block_capacity * bigger_data_code_word_capacity
    return data_code_word_capacity

def DecideVersion(data_code, error_correction_level):
    for version in range(1, 41):
        if len(data_code) <= DataCodeWordCapacity(version, error_correction_level):
            return version
    raise LengthError("Input string is too long")

def DivideCodePer8Bit(code):
    def ListToBit(l):
        res = 0
        for i, v in enumerate(l):
            res += int(v) << (7 - i)
        return res

    assert len(code) % 8 == 0, "Code must be aligned"
    res = []
    for i in range(0, len(code), 8):
        word = ListToBit(code[i : i + 8])
        res.append(word)
    return res

def PaddingDataCode(data_code, version, error_correction_level):
    data_code.extend([False] * (8 - len(data_code) % 8))
    padding_first = True
    for _ in range(DataCodeWordCapacity(version, error_correction_level) - len(data_code) // 8):
        if padding_first:
            data_code.extend([True, True, True, False, True, True, False, False])
        else:
            data_code.extend([False, False, False, True, False, False, False, True])
        padding_first = not padding_first
    return data_code

def DivideIntoCodeBlock(data_code_words, version, error_correction_level):
    (smaller_block_capacity, smaller_data_code_word_capacity),\
    (bigger_block_capacity, bigger_data_code_word_capacity) =\
        BlockInfo(version, error_correction_level)
    data_code_blocks = []
    i = 0
    for _ in range(smaller_block_capacity):
        data_code_blocks.append(data_code_words[i:i + smaller_data_code_word_capacity])
        i += smaller_data_code_word_capacity
    for _ in range(bigger_block_capacity):
        data_code_blocks.append(data_code_words[i:i + bigger_data_code_word_capacity])
        i += bigger_data_code_word_capacity
    return data_code_blocks


if __name__ == "__main__":
    code = [True] * 7 + [False] * 9
    res = DivideCodePer8Bit(code)
    print(res)
