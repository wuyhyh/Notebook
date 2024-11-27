### LeetCode 第 560 题：和为 K 的子数组 (Subarray Sum Equals K)

#### 代码实现
```python
def subarray_sum(nums, k):
    # 用于存储前缀和及其出现次数的字典
    prefix_sum_count = {0: 1}
    # 初始化当前的前缀和为 0
    current_sum = 0
    # 记录满足条件的子数组数量
    count = 0
    
    # 遍历数组中的每个元素
    for num in nums:
        # 更新当前的前缀和
        current_sum += num
        # 如果 (current_sum - k) 在字典中，说明存在一个子数组和为 k
        if current_sum - k in prefix_sum_count:
            count += prefix_sum_count[current_sum - k]
        # 更新前缀和在字典中的次数
        prefix_sum_count[current_sum] = prefix_sum_count.get(current_sum, 0) + 1
    
    return count

# 示例用法
nums = [1, 1, 1]
k = 2
print(subarray_sum(nums, k))  # 输出: 2
```

#### 解释
1. **前缀和**：前缀和是从数组开头到当前元素的累加和。通过计算前缀和可以快速求解任意子数组的和。
2. **字典记录前缀和出现的次数**：字典 `prefix_sum_count` 记录了当前前缀和出现的次数，以便在计算过程中快速查找是否存在满足条件的前缀和。
3. **核心逻辑**：如果当前的前缀和 `current_sum` 减去目标值 `k` 的结果在字典中存在，说明存在一个子数组，它的和正好为 `k`。

#### 用户问题与回答

**问题 1**：为什么不是 `count += 1`？

**回答**：使用 `count += prefix_sum_count[current_sum - k]` 而不是 `count += 1` 的原因是，有可能前缀和 `current_sum - k` 出现过不止一次。这意味着存在多个子数组，它们的和都等于 `k`。通过记录每个前缀和出现的次数，`prefix_sum_count[current_sum - k]` 可以告诉我们有多少个子数组满足条件，因此需要将这些次数全部加到 `count` 中，而不仅仅是加 1。

**问题 2**：`prefix_sum_count[current_sum] = prefix_sum_count.get(current_sum, 0) + 1` 这行代码是什么意思？

**回答**：`get()` 方法有两个参数，第一个参数是要查找的键，第二个参数是默认值。如果字典中没有找到这个键，`get()` 方法就会返回默认值 `0`。这行代码用于更新字典中 `current_sum` 的出现次数。如果当前的前缀和 `current_sum` 在字典中已经存在，就加 1，否则就初始化为 `1`。这样做是为了动态维护每个前缀和的出现次数，方便后续查找和判断。

#### 复杂度分析
- **时间复杂度**: O(n)，其中 n 是数组的长度。每个元素只遍历一次。
- **空间复杂度**: O(n)，用于存储前缀和及其出现次数的字典。
