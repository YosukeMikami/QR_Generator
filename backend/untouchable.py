import data


def SetFinderUntouchable(symbol):
    symbol.untouchable[:9, :9] = True
    symbol.untouchable[-8:, :9] = True
    symbol.untouchable[:9, -8:] = True


def SetTimingUntouchable(symbol):
    for i in range(8, symbol.side_len - 8):
        symbol.untouchable[i, 6] = True
    for i in range(8, symbol.side_len - 8):
        symbol.untouchable[6, i] = True


def SetAlignmentUntouchable(symbol):
    coordinates = data.AlignmentCoordinate(symbol.version)
    coordinate_len = len(coordinates)
    for i in range(coordinate_len):
        for j in range(coordinate_len):
            if not ((i, j) == (0, 0) or (i, j) == (0, coordinate_len - 1) or (i, j) == (coordinate_len - 1, 0)):
                symbol.untouchable[coordinates[i] - 2:coordinates[i] + 3, coordinates[j] - 2:coordinates[j] + 3] = True


def SetVersionInfoUntouchable(symbol):
    if symbol.version <= 6:
        return
    symbol.untouchable[:6, -11:-8] = True
    symbol.untouchable[-11:-8, :6] = True


def SetUntouchable(symbol):
    SetFinderUntouchable(symbol)
    SetTimingUntouchable(symbol)
    SetAlignmentUntouchable(symbol)
    SetVersionInfoUntouchable(symbol)
