LeetCode第300题是《最长递增子序列》（Longest Increasing Subsequence），题目要求给定一个无序整数数组 `nums`，找出其中长度最长的递增子序列，并返回其长度。

### 题目描述

给定一个无序的整数数组 `nums`，找到其中最长递增子序列的长度。

**示例 1：**

```plaintext
输入: nums = [10, 9, 2, 5, 3, 7, 101, 18]
输出: 4
解释: 最长递增子序列是 [2, 3, 7, 101]，因此长度为 4。
```

**示例 2：**

```plaintext
输入: nums = [0, 1, 0, 3, 2, 3]
输出: 4
解释: 最长递增子序列是 [0, 1, 2, 3]，因此长度为 4。
```

**示例 3：**

```plaintext
输入: nums = [7, 7, 7, 7, 7, 7, 7]
输出: 1
解释: 最长递增子序列是 [7]，因此长度为 1。
```

### 解题思路

最长递增子序列问题可以通过 **动态规划** 和 **二分查找** 两种方法来解决。常见的解法是利用 **动态规划**（DP）来求解，另一种更加高效的解法是利用 **二分查找** 和 **贪心算法**。

#### 解法 1：动态规划（O(n^2)）

1. **状态定义**：
    - 定义一个数组 `dp`，其中 `dp[i]` 表示以 `nums[i]` 为结尾的最长递增子序列的长度。

2. **状态转移**：
    - 对于每个 `i`，我们检查前面所有位置的元素 `j`（`0 <= j < i`），如果 `nums[i] > nums[j]`，则可以把 `nums[i]` 加到 `nums[j]` 后面形成一个更长的递增子序列。因此：
      \[
      dp[i] = \max(dp[i], dp[j] + 1)
      \]
    - 最终，最长递增子序列的长度就是 `dp` 数组中的最大值。

3. **时间复杂度**：
    - 时间复杂度是 `O(n^2)`，其中 `n` 是数组 `nums` 的长度。因为对于每个 `i`，我们需要遍历所有前面的 `j`。

#### 解法 2：二分查找（O(n log n)）

这种方法通过 **贪心算法** 和 **二分查找** 来优化时间复杂度。我们维护一个数组 `tails`，其中 `tails[i]` 表示长度为 `i+1` 的递增子序列的最小末尾元素。我们通过 **二分查找** 来找到合适的位置替换 `tails` 数组中的元素，从而构建出一个递增序列。

1. **贪心策略**：
    - 对于每个元素 `num`，使用二分查找找到 `tails` 中第一个大于或等于 `num` 的元素。如果找到该元素，则替换它为 `num`，否则将 `num` 添加到 `tails` 的末尾。

2. **最终答案**：
    - `tails` 数组的长度即为最长递增子序列的长度。

3. **时间复杂度**：
    - 时间复杂度是 `O(n log n)`，其中 `n` 是数组 `nums` 的长度。因为每个元素都要进行一次二分查找。

### 代码实现

#### 解法 1：动态规划（O(n^2)）

```python
def lengthOfLIS(nums):
    if not nums:
        return 0
    
    n = len(nums)
    dp = [1] * n  # 初始化 dp 数组，dp[i] 表示以 nums[i] 为结尾的最长递增子序列的长度
    
    for i in range(1, n):
        for j in range(i):
            if nums[i] > nums[j]:
                dp[i] = max(dp[i], dp[j] + 1)
    
    return max(dp)  # 返回最长递增子序列的长度
```

#### 代码解析：
- **初始化 `dp` 数组**：每个位置的初始值为 1，表示每个元素至少可以作为一个长度为 1 的递增子序列。
- **嵌套循环**：对于每个元素 `i`，我们遍历之前的所有元素 `j`，如果 `nums[i] > nums[j]`，说明可以扩展以 `nums[j]` 为结尾的递增子序列。
- **返回结果**：返回 `dp` 数组中的最大值，即最长递增子序列的长度。

#### 解法 2：二分查找（O(n log n)）

```python
import bisect

def lengthOfLIS(nums):
    tails = []
    
    for num in nums:
        idx = bisect.bisect_left(tails, num)  # 找到 tails 中第一个 >= num 的位置
        
        if idx == len(tails):
            tails.append(num)  # 如果没有找到，说明可以扩展 tails
        else:
            tails[idx] = num  # 如果找到了，更新 tails 中的位置
        
    return len(tails)  # tails 数组的长度即为最长递增子序列的长度
```

#### 代码解析：
- **`tails` 数组**：用于维护递增子序列的最小末尾元素。
- **`bisect_left`**：这是 Python `bisect` 模块提供的一个二分查找函数，用来找到 `tails` 数组中第一个大于或等于当前元素 `num` 的位置。
- **更新 `tails` 数组**：如果找到了合适的位置，则用 `num` 替换掉该位置的值；如果没有找到合适的位置，则将 `num` 添加到 `tails` 的末尾。
- **返回结果**：`tails` 数组的长度即为最长递增子序列的长度。

### 时间复杂度

1. **动态规划（O(n^2)）**：
    - 时间复杂度是 `O(n^2)`，其中 `n` 是数组 `nums` 的长度。对于每个元素 `i`，我们要遍历所有前面的元素 `j`。
    - 空间复杂度是 `O(n)`，用于存储 `dp` 数组。

2. **二分查找（O(n log n)）**：
    - 时间复杂度是 `O(n log n)`，其中 `n` 是数组 `nums` 的长度。对于每个元素，我们要进行一次二分查找。
    - 空间复杂度是 `O(n)`，用于存储 `tails` 数组。

### 示例解析

#### 示例 1：`nums = [10, 9, 2, 5, 3, 7, 101, 18]`

1. **动态规划解法**：
    - 初始化 `dp = [1, 1, 1, 1, 1, 1, 1, 1]`。
    - 对于每个 `i`，我们检查前面所有的 `j`，逐步更新 `dp` 数组。
    - 最终 `dp = [1, 1, 1, 2, 2, 3, 4, 4]`。
    - 返回 `max(dp) = 4`。

2. **二分查找解法**：
    - 初始化 `tails = []`。
    - 对于每个元素，使用二分查找在 `tails` 中找到合适的位置并进行更新，最终 `tails = [2, 3, 7, 101]`。
    - 返回 `len(tails) = 4`。

#### 示例 2：`nums = [0, 1, 0, 3, 2, 3]`

1. **动态规划解法**：
    - 初始化 `dp = [1, 1, 1, 1, 1, 1]`。
    - 最终 `dp = [1, 2, 2, 3, 3, 4]`。
    - 返回 `max(dp) = 4`。

2. **二分查找解法**：
    - 初始化 `tails = []`。
    - 最终 `tails = [0, 1, 2, 3]`。
    - 返回 `len(tails) = 4`。

#### 示例 3：`nums = [7, 7, 7, 7, 7, 7, 7]`

1. **动态规划解法**：
    - 初始化 `dp = [1, 1, 1, 1, 1, 1, 1]`。
    - 最终 `dp = [1, 1, 1, 1, 1, 1, 1
