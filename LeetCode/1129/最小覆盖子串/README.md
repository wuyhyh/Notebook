好的，下面是针对 **LeetCode 第 76 题** （最小覆盖子串）问题的总结文档，包含详细的代码、注释、解释以及解题思路。

---

# LeetCode 第 76 题：最小覆盖子串

## 问题描述

给你一个字符串 `s` 和一个字符串 `t`，请你找出 `s` 中最小的覆盖子串，该子串包含了 `t` 中的所有字符，并且返回该最小子串。如果不存在，返回空字符串。

### 示例：

**输入:**
```plaintext
s = "ADOBECODEBANC", t = "ABC"
```

**输出:**
```plaintext
"BANC"
```

**解释**:
- `s = "ADOBECODEBANC"`, `t = "ABC"`。
- 最小覆盖子串是 `"BANC"`。

## 解题思路

### 核心思想

该问题可以通过 **滑动窗口**（Sliding Window）和 **哈希表** 来解决，滑动窗口用来表示当前的子串，而哈希表用于存储目标字符串 `t` 中字符的频率要求。双指针技巧（`left` 和 `right`）将帮助我们有效地扩展和收缩窗口。

### 步骤分析

1. **滑动窗口的构建**：
    - 通过两个指针 `left` 和 `right` 来维护一个窗口，`right` 用于扩展窗口，`left` 用于缩小窗口。

2. **哈希表存储字符频率**：
    - `target_map` 用来存储 `t` 中字符的频率，`window_map` 用来存储当前窗口中字符的频率。

3. **有效窗口的条件**：
    - 当窗口中包含了 `t` 中的所有字符，并且这些字符的频率都满足要求时，窗口为有效窗口。

4. **窗口缩小**：
    - 当窗口满足条件时，尝试通过移动 `left` 指针来收缩窗口，找到最小的有效窗口。

### `formed` 变量的作用

- **`formed`** 记录当前窗口中已包含的、满足要求的字符种类数。
- **`required`** 是 `t` 中不同字符的种类数，当 `formed == required` 时，表示当前窗口满足条件。

## 代码实现

```python
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
```

## 代码注释说明

### 1. **初始化阶段**：

```python
target_map = Counter(t)  # 统计 t 中每个字符的频率
window_map = Counter()   # 用来统计当前窗口中字符的频率
left = 0                 # 左指针初始化为 0
min_len = float('inf')   # 最小子串的长度初始化为无穷大
min_start = 0            # 最小子串的起始位置
required = len(target_map)  # t 中不同字符的个数
formed = 0               # 当前窗口内已包含的 t 中不同字符的个数
```

- `target_map`：统计字符串 `t` 中每个字符的频率，用于确定目标字符的频率。
- `window_map`：记录当前窗口内字符的频率，帮助判断当前窗口是否包含 `t` 中所有字符。
- `left` 和 `right` 指针表示滑动窗口的左右边界，初始化时均为 0。
- `min_len` 和 `min_start` 用于记录最小覆盖子串的长度和起始位置。
- `required` 为 `t` 中字符的种类数。
- `formed` 为当前窗口中符合要求的字符的种类数。

### 2. **右指针扩展窗口**：

```python
for right in range(len(s)):
    window_map[s[right]] += 1
    if window_map[s[right]] == target_map[s[right]]:
        formed += 1
```

- 右指针 `right` 遍历字符串 `s`，每次扩展窗口，更新 `window_map` 中当前字符的频率。
- 如果当前字符的频率等于 `t` 中该字符的频率，`formed` 增加，表示当前窗口包含了 `t` 中该字符。

### 3. **左指针收缩窗口**：

```python
while formed == required:
    window_len = right - left + 1
    if window_len < min_len:
        min_len = window_len
        min_start = left

    window_map[s[left]] -= 1
    if window_map[s[left]] < target_map[s[left]]:
        formed -= 1
    left += 1
```

- 当 `formed == required` 时，表示当前窗口包含了所有 `t` 中的字符，尝试通过移动左指针来收缩窗口并找到最小的有效窗口。
- 更新最小窗口的长度和起始位置，并通过调整左指针来收缩窗口，直到窗口不再包含 `t` 中所有字符。

### 4. **返回结果**：

```python
if min_len == float('inf'):
    return ""
else:
    return s[min_start:min_start + min_len]
```

- 如果没有找到有效窗口，返回空字符串；否则返回最小覆盖子串。

## 时间复杂度和空间复杂度

- **时间复杂度**：
    - 右指针 `right` 和左指针 `left` 各最多遍历一次整个字符串，因此时间复杂度为 `O(n)`，其中 `n` 是字符串 `s` 的长度。

- **空间复杂度**：
    - 使用两个哈希表 `target_map` 和 `window_map`，其大小分别为 `O(m)` 和 `O(k)`，其中 `m` 是 `t` 中字符的种类数，`k` 是 `s` 中字符的种类数。因此，空间复杂度为 `O(m + k)`。

---

## 总结

通过滑动窗口和哈希表的结合，能够高效地解决这个问题。双指针的策略使得我们能够在一次遍历中找到最小的覆盖子串，同时通过动态更新 `formed` 变量来判断窗口是否有效。这个方法在时间复杂度和空间复杂度上都非常高效，适合处理较大规模的数据。

如果你有任何疑问或需要进一步的解释，请随时告诉我！
