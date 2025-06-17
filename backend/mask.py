from collections import deque

import process


def ApplyMask(symbol, mask_pattern):
    if mask_pattern == 0:
        for i in range(symbol.side_len):
            for j in range(symbol.side_len):
                if not symbol.untouchable[j, i]:
                    if (i + j) % 2 == 0:
                        symbol.symbol[j, i] = not symbol.symbol[j, i]
    elif mask_pattern == 1:
        for i in range(symbol.side_len):
            for j in range(symbol.side_len):
                if not symbol.untouchable[j, i]:
                    if i % 2 == 0:
                        symbol.symbol[j, i] = not symbol.symbol[j, i]
    elif mask_pattern == 2:
        for i in range(symbol.side_len):
            for j in range(symbol.side_len):
                if not symbol.untouchable[j, i]:
                    if j % 3 == 0:
                        symbol.symbol[j, i] = not symbol.symbol[j, i]
    elif mask_pattern == 3:
        for i in range(symbol.side_len):
            for j in range(symbol.side_len):
                if not symbol.untouchable[j, i]:
                    if (i + j) % 3 == 0:
                        symbol.symbol[j, i] = not symbol.symbol[j, i]
    elif mask_pattern == 4:
        for i in range(symbol.side_len):
            for j in range(symbol.side_len):
                if not symbol.untouchable[j, i]:
                    if ((i // 2) + (j // 3)) % 2 == 0:
                        symbol.symbol[j, i] = not symbol.symbol[j, i]
    elif mask_pattern == 5:
        for i in range(symbol.side_len):
            for j in range(symbol.side_len):
                if not symbol.untouchable[j, i]:
                    if (i * j) % 2 + (i * j) % 3 == 0:
                        symbol.symbol[j, i] = not symbol.symbol[j, i]
    elif mask_pattern == 6:
        for i in range(symbol.side_len):
            for j in range(symbol.side_len):
                if not symbol.untouchable[j, i]:
                    if ((i * j) % 2 + (i * j) % 3) % 2 == 0:
                        symbol.symbol[j, i] = not symbol.symbol[j, i]
    else:
        for i in range(symbol.side_len):
            for j in range(symbol.side_len):
                if not symbol.untouchable[j, i]:
                    if ((i + j) % 2 + (i * j) % 3) % 2 == 0:
                        symbol.symbol[j, i] = not symbol.symbol[j, i]


def RestoreMask(symbol, mask_pattern):
    ApplyMask(symbol, mask_pattern)


def SameColorRowColLoss(symbol):
    loss = 0
    for row in range(symbol.side_len):
        color = symbol.symbol[0, row]
        length = 1
        for col in range(1, symbol.side_len):
            if symbol.symbol[col, row] == color:
                length += 1
            else:
                if length >= 5:
                    loss += 3 + (length - 5)
                length = 1
                color = not color
        if length >= 5:
            loss += 3 + (length - 5)
    for col in range(symbol.side_len):
        color = symbol.symbol[col, 0]
        length = 1
        for row in range(1, symbol.side_len):
            if symbol.symbol[col, row] == color:
                length += 1
            else:
                if length >= 5:
                    loss += 3 + (length - 5)
                length = 1
                color = not color
        if length >= 5:
            loss += 3 + (length - 5)
    return loss


def SameColorBlockLoss(symbol):
    loss = 0
    for col in range(symbol.side_len - 1):
        for row in range(symbol.side_len - 1):
            if (symbol.symbol[col, row], symbol.symbol[col, row + 1], symbol.symbol[col + 1, row], symbol.symbol[col + 1, row + 1]) in [(True, True, True, True), (False, False, False, False)]:
                loss += 3
    return loss


def PhonyFinderPatternLoss(symbol):
    for row in range(symbol.side_len):
        len_queue = deque()
        color = symbol.symbol[0, row]
        length = 1
        for col in range(1, symbol.side_len):
            if symbol.symbol[col, row] == color:
                length += 1
            else:
                len_queue.append(length)
                if len(len_queue) > 6:
                    len_queue.popleft()
                if len(len_queue) == 6:
                    base_len = len_queue[1]
                    if len_queue[0] >= 4 * base_len and len_queue[2] == base_len and len_queue[3] == 3 * base_len and len_queue[4] == base_len and len_queue[5] == base_len and not color:
                        return 40
                    if len_queue[0] == base_len and len_queue[2] == 3 * base_len and len_queue[3] == base_len and len_queue[4] == base_len and len_queue[5] >= 4 * base_len and color:
                        return 40
                length = 1
                color = not color
        len_queue.append(length)
        if len(len_queue) > 6:
            len_queue.popleft()
        if len(len_queue) == 6:
            base_len = len_queue[1]
            if len_queue[0] >= 4 * base_len and len_queue[2] == base_len and len_queue[3] == 3 * base_len and len_queue[4] == base_len and len_queue[5] == base_len and not color:
                return 40
            if len_queue[0] == base_len and len_queue[2] == 3 * base_len and len_queue[3] == base_len and len_queue[4] == base_len and len_queue[5] >= 4 * base_len and color:
                return 40
    for col in range(symbol.side_len):
        len_queue = deque()
        color = symbol.symbol[col, 0]
        length = 1
        for row in range(1, symbol.side_len):
            if symbol.symbol[col, row] == color:
                length += 1
            else:
                len_queue.append(length)
                if len(len_queue) > 6:
                    len_queue.popleft()
                if len(len_queue) == 6:
                    base_len = len_queue[1]
                    if len_queue[0] >= 4 * base_len and len_queue[2] == base_len and len_queue[3] == 3 * base_len and len_queue[4] == base_len and len_queue[5] == base_len and color:
                        return 40
                    if len_queue[0] == base_len and len_queue[2] == 3 * base_len and len_queue[3] == base_len and len_queue[4] == base_len and len_queue[5] >= 4 * base_len and not color:
                        return 40
                length = 1
                color = not color
        len_queue.append(length)
        if len(len_queue) > 6:
            len_queue.popleft()
        if len(len_queue) == 6:
            base_len = len_queue[1]
            if len_queue[0] >= 4 * base_len and len_queue[2] == base_len and len_queue[3] == 3 * base_len and len_queue[4] == base_len and len_queue[5] == base_len and not color:
                return 40
            if len_queue[0] == base_len and len_queue[2] == 3 * base_len and len_queue[3] == base_len and len_queue[4] == base_len and len_queue[5] >= 4 * base_len and color:
                return 40
    return 0


def ColorPotionLoss(symbol):
    black_count = 0
    white_count = 0
    for col in range(symbol.side_len):
        for row in range(symbol.side_len):
            if symbol.symbol[col, row]:
                black_count += 1
            else:
                white_count += 1
    black_potion = black_count / (black_count + white_count) * 100
    loss = int(abs(black_potion - 50)) // 5 * 10
    return loss


def EvalMask(symbol, mask):
    ApplyMask(symbol, mask)
    loss = SameColorRowColLoss(symbol) + SameColorBlockLoss(symbol) + PhonyFinderPatternLoss(symbol) + ColorPotionLoss(symbol)
    RestoreMask(symbol, mask)
    return loss


def SelectMask(symbol):
    process.PrintProcess("Selecting mask pattern...(1/8)", 0, 8)
    min_loss = EvalMask(symbol, 0)
    min_pattern = 0
    for i in range(1, 8):
        process.PrintProcess(f"Selecting mask pattern...({i + 1}/8)", i, 8)
        loss = EvalMask(symbol, i)
        if loss < min_loss:
            min_loss = loss
            min_pattern = i
    return min_pattern
