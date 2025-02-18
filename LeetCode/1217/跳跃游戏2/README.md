LeetCode第45题是《跳跃游戏 II》（Jump Game II），题目要求给定一个非负整数数组 `nums`，每个元素表示从该位置可以跳跃的最大步数，求最小的跳跃次数以到达数组的最后一个位置。

### 题目描述
给定一个非负整数数组 `nums`，其中每个元素表示从该位置可以跳跃的最大步数，返回到达最后一个位置的最小跳跃次数。

### 示例
```plaintext
输入: nums = [2,3,1,1,4]
输出: 2
解释: 跳跃次数最小为 2。
从索引 0 跳到 1，再从索引 1 跳到最后一个位置。
```

### 解题思路

这个问题可以通过贪心算法解决。我们在每一跳中选择最远的位置，并在每次跳跃时计算当前能到达的最远位置，直到到达数组的最后一个位置。

### 贪心算法步骤
1. **维护变量**：
    - `jumps`：表示跳跃次数。
    - `current_end`：表示当前跳跃的范围。
    - `farthest`：表示当前可以跳跃到的最远位置。

2. **遍历数组**：
    - 对于数组中的每个元素，更新 `farthest`，即当前位置加上当前位置的跳跃长度。
    - 如果遍历到的位置 `i` 到达 `current_end`，意味着需要增加一个跳跃次数，同时更新 `current_end` 为 `farthest`。

3. **终止条件**：
    - 如果 `current_end` 已经覆盖了数组的最后一个位置，则停止。

### 代码实现（Python）
```python
def jump(nums):
    jumps = 0
    current_end = 0
    farthest = 0
    for i in range(len(nums) - 1):  # 不需要跳到最后一个位置
        farthest = max(farthest, i + nums[i])  # 更新能到达的最远位置
        if i == current_end:  # 到达当前跳跃范围的最后一个位置
            jumps += 1  # 增加跳跃次数
            current_end = farthest  # 更新当前跳跃范围
            if current_end >= len(nums) - 1:  # 如果已经到达或超过最后一个位置
                break
    return jumps
```

### 时间复杂度
- 时间复杂度是 `O(n)`，其中 `n` 是数组 `nums` 的长度。我们只需要遍历一次数组。

### 空间复杂度
- 空间复杂度是 `O(1)`，只使用了常数空间来存储变量。

### 例子解析
以 `nums = [2, 3, 1, 1, 4]` 为例：

- 初始时，`jumps = 0`，`current_end = 0`，`farthest = 0`。
- 第1步，遍历到 `i = 0`，更新 `farthest = max(0, 0 + 2) = 2`。
- 遍历到 `i = 1`，`farthest` 更新为 `max(2, 1 + 3) = 4`，`i == current_end`，增加跳跃次数，`jumps = 1`，更新 `current_end = 4`，已经到达最后位置，跳出循环。

结果：最少跳跃次数为 2。
