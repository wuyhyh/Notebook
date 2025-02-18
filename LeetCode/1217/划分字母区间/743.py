def partitionLabels(s: str):
    # 记录每个字母最后一次出现的位置
    last_pos = {char: idx for idx, char in enumerate(s)}

    result = []
    start = 0  # 当前子串的开始位置
    end = 0    # 当前子串的结束位置

    for i, char in enumerate(s):
        end = max(end, last_pos[char])  # 更新当前子串的结束位置
        if i == end:  # 如果到达当前子串的结束位置
            result.append(i - start + 1)  # 划分出一个子串
            start = i + 1  # 更新下一子串的起始位置

    return result
