from collections import Counter

def minWindow(s, t):
    # 如果 t 的长度大于 s，直接返回空字符串
    if len(t) > len(s):
        return ""

    # target_map 统计 t 中每个字符的频率
    target_map = Counter(t)
    # window_map 用来存储当前滑动窗口中字符的频率
    window_map = Counter()

    # 左指针和右指针初始化，左右指针都指向字符串的开始
    left = 0
    # 用来记录最小子串的长度，初始化为一个很大的值
    min_len = float('inf')
    # 用来记录最小子串的起始位置
    min_start = 0
    # 统计 t 中不同字符的个数，这个值是固定的
    required = len(target_map)
    # 记录当前窗口内已包含的 t 中不同字符的个数
    formed = 0

    # 遍历字符串 s，通过右指针不断扩展窗口
    for right in range(len(s)):
        # 将当前字符加入窗口，更新窗口中的字符频率
        window_map[s[right]] += 1

        # 如果当前字符的频率等于 t 中该字符的频率，增加 formed
        if window_map[s[right]] == target_map[s[right]]:
            formed += 1

        # 当窗口中已经包含了 t 中所有字符时，尝试缩小窗口（即移动左指针）
        while formed == required:
            # 计算当前窗口的长度
            window_len = right - left + 1

            # 更新最小窗口的起始位置和长度
            if window_len < min_len:
                min_len = window_len
                min_start = left

            # 收缩左边界，准备尝试找到一个更小的窗口
            window_map[s[left]] -= 1
            if window_map[s[left]] < target_map[s[left]]:
                formed -= 1
            left += 1

    # 如果 min_len 仍然是初始的无穷大，说明没有找到符合条件的子串，返回空字符串
    if min_len == float('inf'):
        return ""
    else:
        # 返回最小的覆盖子串
        return s[min_start:min_start + min_len]
