### LeetCode 第 128 题：最长连续序列 (Longest Consecutive Sequence)

#### 题目描述
给定一个未排序的整数数组，找出其中最长连续序列的长度。要求算法的时间复杂度为 O(n)。

**示例:**

输入: `[100, 4, 200, 1, 3, 2]`

输出: `4`

解释: 最长的连续序列是 `[1, 2, 3, 4]`，它的长度为 `4`。

#### 解题思路
为了找到最长的连续序列，可以使用集合 (`set`) 来提高查找的效率。核心思想是从每个数字出发，只在这个数字是序列起点的情况下，开始查找连续的序列，从而避免重复计算。

该算法的时间复杂度为 O(n)，因为每个数字最多被访问两次，一次用于判断是否为序列起点，一次用于查找连续序列。

#### 代码实现
```python
def longest_consecutive(nums):
    # 如果输入列表为空，则返回 0，因为没有连续序列
    if not nums:
        return 0
    
    # 将列表转换为集合，以便进行 O(1) 时间复杂度的查找
    num_set = set(nums)
    longest_streak = 0
    
    # 遍历集合中的每个数字
    for num in num_set:
        # 只有当 'num' 是序列的开始时才进行计数
        # 这样可以确保每个序列只被统计一次
        if num - 1 not in num_set:
            current_num = num
            current_streak = 1
            
            # 通过递增 'current_num' 来计算当前序列的长度
            # 直到找不到更多的连续数字
            while current_num + 1 in num_set:
                current_num += 1
                current_streak += 1
            
            # 更新目前找到的最长序列长度
            longest_streak = max(longest_streak, current_streak)
    
    # 返回最长连续序列的长度
    return longest_streak

# 示例用法
nums = [100, 4, 200, 1, 3, 2]
print(longest_consecutive(nums))  # 输出: 4
```

#### 复杂度分析
- **时间复杂度**: O(n)，其中 n 是数组中的元素数量。使用集合来查找元素，确保每个元素只被访问一次。
- **空间复杂度**: O(n)，用于存储数组中的元素。

#### 总结
这道题通过使用集合来提高查找效率，并且通过判断序列的起点来避免重复计算，成功实现了 O(n) 时间复杂度的解法。
