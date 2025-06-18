import data
import encode
import errorcode
import errorcorrectiondata as ecd
import mask
import matplotlib.pyplot as plt
import qrprint
import numpy as np
import seaborn as sns
import untouchable
import midcode


class Symbol:
    def __init__(self, version):
        self.version = version
        self.side_len = data.SideLen(version)
        self.symbol = np.full((self.side_len, self.side_len), False)
        self.untouchable = np.full((self.side_len, self.side_len), False)
        self.position = np.array([self.side_len - 1, self.side_len - 1])


def main(input_string):
    error_correction_level = ecd.Level.kM
    data_code = encode.Encode(input_string)
    data_code_blocks, version = midcode.FormatCodeData4ECC(data_code, error_correction_level)
    error_code_blocks = errorcode.GenerateErrorCodeBlocks(data_code_blocks, version, error_correction_level)

    symbol = Symbol(version)
    untouchable.SetUntouchable(symbol)
    qrprint.PrintWholeCode(symbol, data_code_blocks, error_code_blocks)

    mask_pattern = mask.SelectMask(symbol)
    mask.ApplyMask(symbol, mask_pattern)

    qrprint.PrintFunctionPattern(symbol)
    qrprint.PrintFormatInfo(symbol, encode.EncodeFormatInfo(error_correction_level, mask_pattern))
    qrprint.PrintVersionInfo(symbol, encode.EncodeVersionInfo(version))

    plt.figure()
    sns.heatmap(symbol.symbol.T, cbar=False, square=True, cmap="binary")
    plt.axis("off")
    plt.savefig("fig.png")

if __name__ == "__main__":
    main(input())