LeetCode第5题是《最长回文子串》（Longest Palindromic Substring），题目要求给定一个字符串 `s`，找到 `s` 中最长的回文子串。

---

### 题目描述

给定一个字符串 `s`，返回 `s` 中最长的回文子串。

**示例 1：**

```plaintext
输入: s = "babad"
输出: "bab"
解释: "aba" 同样是一个有效答案。
```

**示例 2：**

```plaintext
输入: s = "cbbd"
输出: "bb"
```

**示例 3：**

```plaintext
输入: s = "a"
输出: "a"
```

**示例 4：**

```plaintext
输入: s = "ac"
输出: "a"
```

---

### 解题思路

这个问题的本质是寻找字符串中的回文中心，然后从中心向两边扩展。我们可以使用以下两种常见的方法来解决。

---

#### 解法 1：中心扩展法

1. **思路**：
    - 回文的中心可能是一个字符（如 `"aba"`）或两个字符之间（如 `"abba"`）。
    - 遍历每个字符，以其为中心，向两边扩展，找到最长的回文子串。
    - 每次扩展时，检查左边和右边的字符是否相等。

2. **时间复杂度**：
    - 遍历每个字符 `O(n)`，每次扩展最多需要 `O(n)`，因此总时间复杂度为 `O(n^2)`。

3. **实现代码**：

```python
def longestPalindrome(s):
    if not s:
        return ""
    
    def expandAroundCenter(left, right):
        while left >= 0 and right < len(s) and s[left] == s[right]:
            left -= 1
            right += 1
        return left + 1, right - 1
    
    start, end = 0, 0
    for i in range(len(s)):
        # 单字符中心
        left1, right1 = expandAroundCenter(i, i)
        # 双字符中心
        left2, right2 = expandAroundCenter(i, i + 1)
        
        # 更新最长回文子串的范围
        if right1 - left1 > end - start:
            start, end = left1, right1
        if right2 - left2 > end - start:
            start, end = left2, right2
    
    return s[start:end + 1]
```

---

#### 解法 2：动态规划

1. **思路**：
    - 定义一个二维布尔数组 `dp[i][j]`，表示子串 `s[i:j+1]` 是否是回文。
    - 如果 `s[i] == s[j]` 且子串 `s[i+1:j]` 是回文，则 `s[i:j+1]` 是回文。
    - 状态转移方程：
      \[
      dp[i][j] = (s[i] == s[j]) \, \text{and} \, (j-i < 3 \, \text{or} \, dp[i+1][j-1])
      \]
    - 遍历时从小区间向大区间扩展。

2. **时间复杂度**：
    - 状态转移需要遍历所有可能的子串，总复杂度为 `O(n^2)`。

3. **实现代码**：

```python
def longestPalindrome(s):
    if not s:
        return ""
    
    n = len(s)
    dp = [[False] * n for _ in range(n)]
    start, max_len = 0, 0
    
    for j in range(n):
        for i in range(j + 1):
            if s[i] == s[j] and (j - i < 3 or dp[i + 1][j - 1]):
                dp[i][j] = True
                if j - i + 1 > max_len:
                    start = i
                    max_len = j - i + 1
    
    return s[start:start + max_len]
```

---

### 示例解析

#### 示例 1：`s = "babad"`

1. **中心扩展法**：
    - `i = 0`：中心为 `"b"`，扩展得 `"bab"`。
    - `i = 1`：中心为 `"a"`，扩展得 `"aba"`。
    - `i = 2`：中心为 `"b"`，扩展得 `"bab"`。
    - 最终结果：`"bab"` 或 `"aba"`。

2. **动态规划法**：
    - 初始化 `dp` 数组。
    - 更新 `dp`，最长回文子串为 `"bab"` 或 `"aba"`。

---

#### 示例 2：`s = "cbbd"`

1. **中心扩展法**：
    - `i = 0`：中心为 `"c"`，扩展得 `"c"`。
    - `i = 1`：中心为 `"b"`，扩展得 `"bb"`。
    - 最终结果：`"bb"`。

2. **动态规划法**：
    - 初始化 `dp` 数组。
    - 更新 `dp`，最长回文子串为 `"bb"`。

---

### 总结

| 方法           | 时间复杂度 | 空间复杂度 | 适用场景 |
|----------------|------------|------------|----------|
| 中心扩展法     | `O(n^2)`   | `O(1)`     | 简单实现 |
| 动态规划       | `O(n^2)`   | `O(n^2)`   | 需要记录状态，适合分析子串属性 |

中心扩展法在实现上更简单，动态规划方法更适合需要保留状态信息的场景。
