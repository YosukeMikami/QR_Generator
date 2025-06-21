import data
import matplotlib.pyplot as plt
import seaborn as sns
import io


def PrintFinderPattern(symbol):
    centers = [[3, 3], [symbol.side_len - 4, 3], [3, symbol.side_len - 4]]
    for c in centers:
        symbol.symbol[c[0] - 3:c[0] + 4, c[1] - 3:c[1] + 4] = True
        symbol.symbol[c[0] - 2:c[0] + 3, c[1] - 2:c[1] + 3] = False
        symbol.symbol[c[0] - 1:c[0] + 2, c[1] - 1:c[1] + 2] = True


def PrintTimingPattern(symbol):
    for i in range(8, symbol.side_len - 8):
        if i % 2 == 0:
            symbol.symbol[i, 6] = True
        else:
            symbol.symbol[i, 6] = False
    for i in range(8, symbol.side_len - 8):
        if i % 2 == 0:
            symbol.symbol[6, i] = True
        else:
            symbol.symbol[6, i] = False


def PrintAlignmentPattern(symbol):
    coordinates = data.AlignmentCoordinate(symbol.version)
    coordinate_len = len(coordinates)
    for i in range(coordinate_len):
        for j in range(coordinate_len):
            if not ((i, j) == (0, 0) or (i, j) == (0, coordinate_len - 1) or (i, j) == (coordinate_len - 1, 0)):
                symbol.symbol[coordinates[i] - 2:coordinates[i] + 3, coordinates[j] - 2:coordinates[j] + 3] = True
                symbol.symbol[coordinates[i] - 1:coordinates[i] + 2, coordinates[j] - 1:coordinates[j] + 2] = False
                symbol.symbol[coordinates[i], coordinates[j]] = True


def PrintFormatInfo(symbol, info):
    i = 0
    for j in range(9):
        if j == 6:
            continue
        symbol.symbol[8, j] = (info >> i) & 1 == 1
        i += 1
    for j in range(7, -1, -1):
        if j == 6:
            continue
        symbol.symbol[j, 8] = (info >> i) & 1 == 1
        i += 1
    i = 0
    for j in range(symbol.side_len - 1, symbol.side_len - 9, -1):
        symbol.symbol[j, 8] = (info >> i) & 1 == 1
        i += 1
    symbol.symbol[8, -8] = True
    for j in range(symbol.side_len - 7, symbol.side_len):
        symbol.symbol[8, j] = (info >> i) & 1 == 1
        i += 1


def PrintVersionInfo(symbol, info=None):
    if info is None or symbol.version <= 6:
        return
    i = 0
    for j in range(6):
        for k in range(-11, -8):
            symbol.symbol[k, j] = (info >> i) & 1 == 1
            i += 1
    i = 0
    for j in range(6):
        for k in range(-11, -8):
            symbol.symbol[j, k] = (info >> i) & 1 == 1
            i += 1


def PrintCode(symbol, code, len):
    i = 0
    while (i < len):
        if not symbol.untouchable[symbol.position[0], symbol.position[1]]:
            symbol.symbol[symbol.position[0], symbol.position[1]] = (code >> (len - i - 1)) & 1 == 1
            i += 1
        if symbol.position[0] > 6:
            if (symbol.side_len - 1 - symbol.position[0]) % 2 == 0:
                symbol.position[0] -= 1
            elif (symbol.side_len - 1 - symbol.position[0]) % 4 == 1:
                if symbol.position[1] == 0:
                    if symbol.position[0] == 7:
                        symbol.position[0] = 5
                    else:
                        symbol.position[0] -= 1
                else:
                    symbol.position[0] += 1
                    symbol.position[1] -= 1
            else:
                if symbol.position[1] == symbol.side_len - 1:
                    symbol.position[0] -= 1
                else:
                    symbol.position[0] += 1
                    symbol.position[1] += 1
        else:
            if symbol.position[0] % 4 == 0:
                if symbol.position[1] == symbol.side_len - 1:
                    symbol.position[0] -= 1
                else:
                    symbol.position[0] += 1
                    symbol.position[1] += 1
            elif symbol.position[0] % 4 == 2:
                if symbol.position[1] == 0:
                    symbol.position[0] -= 1
                else:
                    symbol.position[0] += 1
                    symbol.position[1] -= 1
            else:
                symbol.position[0] -= 1


def PrintFunctionPattern(symbol):
    PrintFinderPattern(symbol)
    PrintTimingPattern(symbol)
    PrintAlignmentPattern(symbol)


def PrintWholeCode(symbol, data_code_blocks, error_code_blocks):
    updated = True
    data_index = 0
    while updated:
        updated = False
        for block_index in range(len(data_code_blocks)):
            if len(data_code_blocks[block_index]) > data_index:
                PrintCode(symbol, data_code_blocks[block_index][data_index], 8)
                updated = True
        if not updated:
            break
        data_index += 1
    updated = True
    error_index = 0
    while updated:
        updated = False
        for block_index in range(len(error_code_blocks)):
            if len(error_code_blocks[block_index]) > error_index:
                PrintCode(symbol, error_code_blocks[block_index][error_index], 8)
                updated = True
        if not updated:
            break
        error_index += 1


def OutputQRAsImage(symbol, size, output_file):
    plt.figure(figsize=(size, size))
    sns.heatmap(symbol.symbol.T, cbar=False, square=True, cmap="binary")
    # plt.imshow(symbol.symbol.T, cmap="binary", interpolation="nearest")
    quiet_zone_ratio = 4 / (symbol.symbol.shape[0] + 8)
    plt.subplots_adjust(
        left = quiet_zone_ratio,
        right = 1 - quiet_zone_ratio,
        bottom = quiet_zone_ratio,
        top = 1 - quiet_zone_ratio
    )
    plt.axis("off")
    plt.savefig(output_file)


def OutputQRAsBlob(symbol, size, format):
    plt.figure(figsize=(size, size))
    sns.heatmap(symbol.symbol.T, cbar=False, square=True, cmap="binary")
    quiet_zone_ratio = 4 / (symbol.symbol.shape[0] + 8)
    plt.subplots_adjust(
        left = quiet_zone_ratio,
        right = 1 - quiet_zone_ratio,
        bottom = quiet_zone_ratio,
        top = 1 - quiet_zone_ratio
    )
    plt.axis("off")

    buf = io.BytesIO()
    plt.savefig(buf, format=format)
    plt.close()
    buf.seek(0)
    return buf
