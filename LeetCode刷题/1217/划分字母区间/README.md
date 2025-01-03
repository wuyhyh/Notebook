LeetCode第763题是《划分字母区间》（Partition Labels），题目要求给定一个字符串 `s`，将字符串分割成若干个子字符串，使得每个字母只出现在一个子字符串中，并且返回一个列表，表示每个子字符串的长度。

### 题目描述
你需要将字符串 `s` 划分成尽可能多的子串，使得每个字母都出现在一个子串中，并且返回一个列表，列表中的每个元素表示一个子串的长度。

### 示例

```plaintext
输入: s = "abac"
输出: [4]
解释: "a"出现在第1个子串中，"b"出现在第2个子串中，"c"出现在第3个子串中。每个子串的字母都是唯一的。
```

```plaintext
输入: s = "eccbbbbdec"
输出: [3, 5, 1]
解释: 划分子串为 "e", "ccbbb", "dec"。
```

### 解题思路

我们可以通过贪心算法来解决这个问题。关键在于每个字母的最右出现位置（即字母最后一次出现的索引）。如果在遍历过程中我们遇到一个字母，而它的最后一次出现位置还未被遍历到，则将该字母加入当前子串中。

### 解题步骤

1. **计算每个字母的最后一次出现位置**：
   遍历字符串 `s`，记录每个字母最后一次出现的位置。

2. **遍历字符串并划分子串**：
   使用两个变量 `start` 和 `end` 来表示当前子串的范围。
    - 对于当前字符 `s[i]`，更新 `end` 为该字符最后一次出现的位置。
    - 如果当前索引 `i` 等于 `end`，则说明当前子串已经划分完毕，可以将子串的长度（`end - start + 1`）加入结果列表，并将 `start` 更新为 `i + 1`，准备处理下一个子串。

3. **返回结果**：
   最终返回所有子串的长度。

### 代码实现（Python）

```python
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
```

### 时间复杂度
- 时间复杂度是 `O(n)`，其中 `n` 是字符串 `s` 的长度。第一次遍历字符串 `s` 来计算每个字母的最后出现位置，然后第二次遍历字符串来划分子串，都是线性时间复杂度。

### 空间复杂度
- 空间复杂度是 `O(n)`，我们需要额外存储每个字母的最后出现位置。

### 例子解析

以 `s = "eccbbbbdec"` 为例：
1. 计算每个字母的最后出现位置：
    - `'e'` 最后出现的位置是 9
    - `'c'` 最后出现的位置是 8
    - `'b'` 最后出现的位置是 7
    - `'d'` 最后出现的位置是 6

2. 遍历字符串：
    - `i = 0`，`char = 'e'`，`end = 9`（更新结束位置）
    - `i = 1`，`char = 'c'`，`end = 9`
    - `i = 2`，`char = 'c'`，`end = 9`
    - `i = 3`，`char = 'b'`，`end = 9`
    - `i = 4`，`char = 'b'`，`end = 9`
    - `i = 5`，`char = 'b'`，`end = 9`
    - `i = 6`，`char = 'b'`，`end = 9`
    - `i = 7`，`char = 'd'`，`end = 9`
    - `i = 8`，`char = 'e'`，`end = 9`
    - `i = 9`，`char = 'c'`，`end = 9`，到达子串的结束位置，划分一个子串 `[3, 5, 1]`。

结果返回 `[3, 5, 1]`。

这样就完成了划分字母区间的任务！
