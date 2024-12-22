LeetCode第139题是《单词拆分》（Word Break），题目要求给定一个字符串 `s` 和一个包含一些词语的字典 `wordDict`，判断字符串 `s` 是否可以被空格拆分为一个或多个字典中的单词。

### 题目描述

给定一个非空字符串 `s` 和一个包含非空单词的字典 `wordDict`，判断 `s` 是否可以被拆分为一个或多个字典中的单词。

**示例 1：**

```plaintext
输入: s = "leetcode", wordDict = ["leet", "code"]
输出: true
解释: 返回 true 因为 "leetcode" 可以被拆分成 "leet" 和 "code"。
```

**示例 2：**

```plaintext
输入: s = "applepenapple", wordDict = ["apple", "pen"]
输出: true
解释: 返回 true 因为 "applepenapple" 可以被拆分成 "apple", "pen", "apple"。
```

**示例 3：**

```plaintext
输入: s = "catsandog", wordDict = ["cats", "dog", "sand", "and", "cat"]
输出: false
```

### 解题思路

这个问题可以通过**动态规划**来解决。我们需要判断给定的字符串 `s` 是否能被字典中的单词组合成。

#### 动态规划思想：

1. **定义状态**：
    - 定义一个布尔数组 `dp`，其中 `dp[i]` 表示字符串 `s[0:i]`（即 `s` 的前 `i` 个字符）是否可以拆分为字典中的单词。
    - 初始化 `dp[0] = True`，表示空字符串可以拆分（没有任何单词）。

2. **状态转移**：
    - 对于每个 `i`，遍历所有 `j`，如果 `dp[j]` 为 `True` 且 `s[j:i]` 是字典中的单词，则 `dp[i]` 应该设置为 `True`。

   具体来说，对于每个位置 `i`，我们从 `i-1` 向前遍历，检查是否存在一个位置 `j`，使得 `dp[j] = True` 且 `s[j:i]` 属于字典。如果满足这些条件，那么 `dp[i] = True`。

3. **最终结果**：
    - `dp[len(s)]` 就是最终的答案。如果 `dp[len(s)]` 为 `True`，则说明整个字符串 `s` 可以通过字典中的单词组成；否则，返回 `False`。

### 代码实现

```python
def wordBreak(s, wordDict):
    wordSet = set(wordDict)  # 将字典转换为集合，查找更高效
    n = len(s)
    
    # dp[i] 表示 s[0:i] 是否能由字典中的单词组成
    dp = [False] * (n + 1)
    dp[0] = True  # 空字符串可以拆分
    
    # 遍历所有可能的子串
    for i in range(1, n + 1):
        for j in range(i):
            if dp[j] and s[j:i] in wordSet:
                dp[i] = True
                break
    
    return dp[n]
```

### 代码解析

1. **初始化**：
    - `wordSet = set(wordDict)`：将字典转换为集合，以便进行高效的查找。
    - `dp = [False] * (n + 1)`：定义 `dp` 数组，其中 `dp[i]` 表示字符串 `s[0:i]` 是否可以拆分为字典中的单词。初始化时，`dp[0] = True`，表示空字符串可以拆分。

2. **动态规划遍历**：
    - 遍历 `i` 从 `1` 到 `n`，对于每个 `i`，遍历所有 `j`（`0 <= j < i`），检查是否存在一个 `j`，使得 `dp[j]` 为 `True` 且 `s[j:i]` 是字典中的单词。
    - 如果满足条件，设置 `dp[i] = True`，并结束内层循环，跳到下一个 `i`。

3. **返回结果**：
    - 最终的结果保存在 `dp[n]` 中，表示整个字符串 `s` 是否可以由字典中的单词组成。

### 时间复杂度

- **时间复杂度**：`O(n^2)`，其中 `n` 是字符串 `s` 的长度。我们遍历每个位置 `i`，对于每个 `i`，遍历所有 `j`，所以总时间复杂度为 `O(n^2)`。

- **空间复杂度**：`O(n)`，我们使用一个大小为 `n+1` 的 `dp` 数组。

### 示例解析

#### 示例 1：`s = "leetcode", wordDict = ["leet", "code"]`

1. **初始化**：
    - `dp = [True, False, False, False, False, False, False, False, False]`

2. **动态规划过程**：
    - `i = 1`：无法构成任何字典中的单词，`dp[1] = False`。
    - `i = 2`：同样无法构成，`dp[2] = False`。
    - `i = 3`：依然无法构成，`dp[3] = False`。
    - `i = 4`：`dp[0] = True` 且 `s[0:4] = "leet"` 在字典中，`dp[4] = True`。
    - `i = 5` 到 `i = 7`，仍无法构成，`dp[5] = dp[6] = dp[7] = False`。
    - `i = 8`：`dp[4] = True` 且 `s[4:8] = "code"` 在字典中，`dp[8] = True`。

3. **最终结果**：
    - `dp[8] = True`，表示 `s = "leetcode"` 可以被拆分成 "leet" 和 "code"。

#### 示例 2：`s = "applepenapple", wordDict = ["apple", "pen"]`

1. **初始化**：
    - `dp = [True, False, False, False, False, False, False, False, False, False, False, False, False, False, False]`

2. **动态规划过程**：
    - `i = 1` 到 `i = 4`，无法构成任何字典中的单词。
    - `i = 5`：`dp[0] = True` 且 `s[0:5] = "apple"` 在字典中，`dp[5] = True`。
    - `i = 6` 到 `i = 9`，`dp[6] = True` 且 `s[5:9] = "pen"` 在字典中，`dp[9] = True`。
    - `i = 10` 到 `i = 15`，`dp[9] = True` 且 `s[9:15] = "apple"` 在字典中，`dp[15] = True`。

3. **最终结果**：
    - `dp[15] = True`，表示 `s = "applepenapple"` 可以被拆分成 "apple"、"pen" 和 "apple"。

#### 示例 3：`s = "catsandog", wordDict = ["cats", "dog", "sand", "and", "cat"]`

1. **初始化**：
    - `dp = [True, False, False, False, False, False, False, False, False]`

2. **动态规划过程**：
    - 对于每个 `i`，没有找到合适的分割方式，最终 `dp[8] = False`。

3. **最终结果**：
    - `dp[8] = False`，表示 `s = "catsandog"` 不能被拆分为字典中的单词。

### 总结

- 该问题通过 **动态规划** 来解决，时间复杂度为 `O(n^2)`，适合中等规模的输入。
- **状态转移** 的关键是通过检查每个子串是否在字典中，依此更新 `dp` 数组，最终判断字符串是否可以由字典中的单词组成。
