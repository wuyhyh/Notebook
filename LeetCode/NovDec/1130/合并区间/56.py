def merge(intervals):
    # 如果区间为空或只有一个区间，直接返回
    if not intervals:
        return []

    # 按照区间的起始位置进行排序
    intervals.sort(key=lambda x: x[0])

    # 初始化合并后的区间列表
    merged = [intervals[0]]

    # 遍历所有区间，进行合并
    for current in intervals[1:]:
        # 获取合并后的最后一个区间
        last = merged[-1]

        # 如果当前区间与最后一个合并区间有重叠，合并它们
        if current[0] <= last[1]:
            last[1] = max(last[1], current[1])
        else:
            # 否则，直接添加当前区间
            merged.append(current)

    return merged
