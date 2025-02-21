### LeetCode 第 438 题：找到字符串中所有字母异位词 (Find All Anagrams in a String)

#### 代码实现
```python
from collections import Counter

def find_anagrams(s: str, p: str):
    # 目标字符串 p 的字符频率，用于后续比较
    p_count = Counter(p)
    # 当前滑动窗口内的字符频率
    current_count = Counter()
    # 存储结果的列表，保存所有找到的异位词的起始索引
    result = []
    
    # 定义窗口的大小为 p 的长度
    p_len = len(p)
    
    # 遍历字符串 s 中的每个字符
    for i in range(len(s)):
        # 将当前字符添加到滑动窗口中，并更新其频率
        current_count[s[i]] += 1
        
        # 如果当前窗口大小超过了 p 的长度，需要移除窗口左侧的字符
        if i >= p_len:
            # 计算需要移除的字符（窗口的左侧字符）
            left_char = s[i - p_len]
            # 如果该字符的频率为 1，直接从字典中删除（节省空间）
            if current_count[left_char] == 1:
                del current_count[left_char]
            else:
                # 如果频率大于 1，则将其频率减少 1
                current_count[left_char] -= 1
        
        # 比较当前窗口的字符频率与目标字符串 p 的字符频率是否相同
        # 如果相同，说明找到了一个字母异位词，记录起始索引
        if current_count == p_count:
            result.append(i - p_len + 1)
    
    # 返回所有找到的异位词起始索引
    return result

# 示例用法
s = "cbaebabacd"
p = "abc"
print(find_anagrams(s, p))  # 输出: [0, 6]
```

#### 解释
1. 使用 Python 的 `Counter` 统计 `p` 中每个字符的频率，作为目标频率。
2. 使用一个滑动窗口遍历 `s`，窗口大小与 `p` 的长度相同。
3. 在遍历过程中，将当前字符加入窗口，并根据窗口大小移除超出的字符。
4. 每次更新窗口后，比较当前窗口与目标字符频率是否相等，相等则记录窗口的起始位置。

#### 复杂度分析
- **时间复杂度**: O(n)，其中 n 是字符串 `s` 的长度。每个字符只需处理一次。
- **空间复杂度**: O(1)，字母的数量是固定的（26 个字母），因此 `Counter` 的大小不超过常数。
