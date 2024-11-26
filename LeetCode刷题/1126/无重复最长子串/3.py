def length_of_longest_substring(s: str) -> int:
    # 创建一个集合来存储当前窗口中的字符
    char_set = set()
    left = 0  # 左指针
    max_len = 0  # 用于存储最长子串的长度

    # 遍历字符串中的每个字符，右指针向右滑动
    for right in range(len(s)):
        # 如果当前字符重复，移动左指针直到不重复
        while s[right] in char_set:
            char_set.remove(s[left])
            left += 1
        # 将当前字符加入集合
        char_set.add(s[right])
        # 更新最长子串的长度
        max_len = max(max_len, right - left + 1)

    return max_len

# 示例用法
s = "abcabcbb"
print(length_of_longest_substring(s))  # 输出: 3