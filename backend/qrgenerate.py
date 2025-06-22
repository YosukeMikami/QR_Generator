import data
import encode
import errorcode
import errorcorrectiondata as ecd
import mask
import qrprint
import numpy as np
import untouchable
import midcode


class Symbol:
    def __init__(self, version):
        self.version = version
        self.side_len = data.SideLen(version)
        self.symbol = np.full((self.side_len, self.side_len), False)
        self.untouchable = np.full((self.side_len, self.side_len), False)
        self.position = np.array([self.side_len - 1, self.side_len - 1])


def main(input_string, error_correction_level, output_file=None, format="png", pixel_num=10, dpi=100,  blob=False):
    assert blob or output_file is not None, "output_file is required when blob is False"
    if isinstance(error_correction_level, str):
        if error_correction_level == "L":
            error_correction_level = ecd.Level.kL
        elif error_correction_level == "H":
            error_correction_level = ecd.Level.kH
        elif error_correction_level == "Q":
            error_correction_level = ecd.Level.kQ
        else:
            error_correction_level = ecd.Level.kM
    # 入力データをエンコード
    data_code = encode.Encode(input_string, error_correction_level)
    data_code_blocks, version = midcode.FormatCodeData4ECC(data_code, error_correction_level)
    # エラー訂正コード生成
    error_code_blocks = errorcode.GenerateErrorCodeBlocks(data_code_blocks, version, error_correction_level)

    # データ描画
    symbol = Symbol(version)
    untouchable.SetUntouchable(symbol)
    qrprint.PrintWholeCode(symbol, data_code_blocks, error_code_blocks)

    # マスキング
    mask_pattern = mask.SelectMask(symbol)
    mask.ApplyMask(symbol, mask_pattern)

    # その他パターン描画
    qrprint.PrintFunctionPattern(symbol)
    qrprint.PrintFormatInfo(symbol, encode.EncodeFormatInfo(error_correction_level, mask_pattern))
    qrprint.PrintVersionInfo(symbol, encode.EncodeVersionInfo(version))

    # 出力
    if blob:
        return qrprint.OutputQRAsBlob(symbol, pixel_num, dpi, format)
    else:
        qrprint.OutputQRAsImage(symbol, pixel_num, dpi, output_file)
        return None

if __name__ == "__main__":
    main(input(), ecd.Level.kL, "fig.png", pixel_num=512, dpi=100)
