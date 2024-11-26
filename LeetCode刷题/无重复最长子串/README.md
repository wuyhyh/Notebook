好的！既然你更喜欢使用 `set()` 的方法，我们可以继续使用那个方法。通过 `set()` 来维护当前窗口的字符集合，可以简化一些逻辑。

回顾一下最初的解法，这种方法利用一个滑动窗口和 `set()` 来记录当前窗口中的字符。当遇到重复字符时，左指针 `start` 向右移动，直到窗口中没有重复字符为止。

### 代码实现：
```python
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
```

### 解释：
1. 使用一个 `set()` 存储当前窗口中的字符，确保没有重复字符。
2. 遍历字符串的每个字符时，如果当前字符在 `set()` 中已经出现过（即重复字符），则将左指针 `left` 向右移动，并从 `set()` 中移除左指针指向的字符，直到窗口内不再有重复字符。
3. 每次更新窗口后，计算当前窗口的长度，并与已有的最长长度 `max_len` 比较，更新 `max_len`。

### 例子
假设 `s = "abcabcbb"`：
- 初始时 `char_set = {}`，`left = 0`，`max_len = 0`
- 第一次右移 `right = 0`，字符 `'a'`，`char_set = {'a'}`，`max_len = 1`
- 第二次右移 `right = 1`，字符 `'b'`，`char_set = {'a', 'b'}`，`max_len = 2`
- 第三次右移 `right = 2`，字符 `'c'`，`char_set = {'a', 'b', 'c'}`，`max_len = 3`
- 第四次右移 `right = 3`，字符 `'a'`，`char_set` 中已经有 `'a'`，所以左指针 `left` 移动到位置 1，`char_set = {'b', 'c', 'a'}`，`max_len` 不变。
- 继续移动右指针，直到字符串遍历结束。

最终的最大子串长度是 `3`，即 `"abc"`。

如果这个方法对你来说更清晰，随时告诉我，如果还有其他问题或者优化建议，也可以继续问！