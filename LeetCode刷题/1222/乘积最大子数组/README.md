LeetCode第152题是《乘积最大子数组》（Maximum Product Subarray），题目要求给定一个整数数组 `nums`，找出一个具有最大乘积的子数组，并返回该乘积。

### 题目描述

给定一个整数数组 `nums`，找到一个具有最大乘积的子数组（子数组的长度至少为 1），并返回该子数组的乘积。

**示例 1：**

```plaintext
输入: nums = [2, 3, -2, 4]
输出: 6
解释: 子数组 [2, 3] 的乘积最大，结果为 6。
```

**示例 2：**

```plaintext
输入: nums = [-2, 0, -1]
输出: 0
解释: 结果为 0，子数组为 [0]。
```

**提示：**

- `1 <= nums.length <= 2 * 10^4`
- `-10 <= nums[i] <= 10`
- 题目数据保证数组中至少有一个元素。

### 解题思路

这个问题可以通过 **动态规划** 来解决。关键点在于，我们不仅需要记录到当前位置的最大乘积，还需要记录最小乘积。

#### 动态规划思想：

1. **状态定义**：
    - 定义两个变量 `max_prod` 和 `min_prod`，分别表示到当前位置为止的最大乘积和最小乘积。
    - 由于乘积中可能会有负数，最小乘积可能会变成最大乘积（例如，负数与负数相乘），因此我们需要同时维护最大和最小乘积。

2. **状态转移**：
    - 对于每个元素 `num`，我们可以从三种情况来更新 `max_prod` 和 `min_prod`：
        - 1. 乘上当前元素 `num`，即 `max_prod = max(num, num * max_prod, num * min_prod)`
        - 2. 乘上当前元素 `num`，即 `min_prod = min(num, num * max_prod, num * min_prod)`
    - 需要特别注意，当当前元素 `num` 为负数时，它可能会使得最小的乘积变得最大。

3. **最终结果**：
    - 遍历结束后，`max_prod` 即为最大的子数组乘积。

### 代码实现

```python
def maxProduct(nums):
    if not nums:
        return 0
    
    max_prod = min_prod = result = nums[0]
    
    for i in range(1, len(nums)):
        if nums[i] < 0:
            max_prod, min_prod = min_prod, max_prod  # 交换最大值和最小值
        
        max_prod = max(nums[i], max_prod * nums[i])
        min_prod = min(nums[i], min_prod * nums[i])
        
        result = max(result, max_prod)
    
    return result
```

### 代码解析：

1. **初始化**：
    - `max_prod = min_prod = result = nums[0]`：初始化 `max_prod` 和 `min_prod` 为数组的第一个元素，因为第一个元素就是子数组的第一个乘积。

2. **遍历数组**：
    - `if nums[i] < 0`: 如果当前元素是负数，则交换 `max_prod` 和 `min_prod`。这是因为负数可能将当前的最小乘积变为最大乘积。
    - `max_prod = max(nums[i], max_prod * nums[i])`：更新 `max_prod` 为当前元素 `nums[i]` 或者乘上当前元素后的值。
    - `min_prod = min(nums[i], min_prod * nums[i])`：更新 `min_prod` 为当前元素 `nums[i]` 或者乘上当前元素后的值。

3. **更新结果**：
    - `result = max(result, max_prod)`：更新结果为 `max_prod` 和当前结果中的最大值。

4. **返回结果**：
    - 最后返回 `result`，即最大乘积。

### 时间复杂度

- **时间复杂度**：`O(n)`，其中 `n` 是数组 `nums` 的长度。我们只需要遍历数组一次，并在每次遍历中进行常数时间的操作。
- **空间复杂度**：`O(1)`，我们只使用常数空间来存储 `max_prod`、`min_prod` 和 `result`。

### 示例解析

#### 示例 1：`nums = [2, 3, -2, 4]`

1. **初始化**：
    - `max_prod = min_prod = result = 2`

2. **遍历过程**：
    - `i = 1`，`num = 3`：
        - `max_prod = max(3, 2 * 3) = 6`
        - `min_prod = min(3, 2 * 3) = 3`
        - `result = max(6, 6) = 6`
    - `i = 2`，`num = -2`：
        - 交换 `max_prod` 和 `min_prod`，`max_prod = 3`, `min_prod = 6`
        - `max_prod = max(-2, 3 * -2) = -6`
        - `min_prod = min(-2, 6 * -2) = -12`
        - `result = max(6, -6) = 6`
    - `i = 3`，`num = 4`：
        - `max_prod = max(4, -6 * 4) = 4`
        - `min_prod = min(4, -12 * 4) = -48`
        - `result = max(6, 4) = 6`

3. **最终结果**：
    - `result = 6`。

#### 示例 2：`nums = [-2, 0, -1]`

1. **初始化**：
    - `max_prod = min_prod = result = -2`

2. **遍历过程**：
    - `i = 1`，`num = 0`：
        - `max_prod = max(0, -2 * 0) = 0`
        - `min_prod = min(0, -2 * 0) = 0`
        - `result = max(0, 0) = 0`
    - `i = 2`，`num = -1`：
        - 交换 `max_prod` 和 `min_prod`，`max_prod = 0`, `min_prod = 0`
        - `max_prod = max(-1, 0 * -1) = 0`
        - `min_prod = min(-1, 0 * -1) = -1`
        - `result = max(0, 0) = 0`

3. **最终结果**：
    - `result = 0`。

#### 示例 3：`nums = [2, -5, -2, -4, 3]`

1. **初始化**：
    - `max_prod = min_prod = result = 2`

2. **遍历过程**：
    - `i = 1`，`num = -5`：
        - 交换 `max_prod` 和 `min_prod`，`max_prod = -2`, `min_prod = 2`
        - `max_prod = max(-5, -2 * -5) = 10`
        - `min_prod = min(-5, 2 * -5) = -10`
        - `result = max(2, 10) = 10`
    - `i = 2`，`num = -2`：
        - 交换 `max_prod` 和 `min_prod`，`max_prod = -10`, `min_prod = 10`
        - `max_prod = max(-2, -10 * -2) = 20`
        - `min_prod = min(-2, 10 * -2) = -20`
        - `result = max(10, 20) = 20`
    - `i = 3`，`num = -4`：
        - 交换 `max_prod` 和 `min_prod`，`max_prod = -20`, `min_prod = 20`
        - `max_prod = max(-4, -20 * -4) = 80`
        - `min_prod = min(-4, 20 * -4) = -80`
        - `result = max(20, 80) = 80`
    - `i = 4`，`num = 3`：
        - `max_prod = max(3, 80 * 3) = 240`
        - `min_prod = min(3, -80 * 3) = -240`
        - `result = max(80, 240) = 240`

3. **最终结果**：
    - `result = 240`。

### 总结

- **动态规划解法**：通过维护 `max_prod` 和 `min_prod` 来同时考虑最大乘积和最小乘积，避免负数干扰。时间复杂度为 `O(n)`，空间复杂度为 `O(1)`。
- **适用场景**：适用于长度较大的数组，并且考虑到
