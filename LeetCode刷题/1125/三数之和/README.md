### LeetCode 第 15 题：三数之和 (Three Sum)

#### 问题描述
给定一个包含 n 个整数的数组 `nums`，判断数组中是否存在三个元素 a，b，c，使得 a + b + c = 0？请找出所有不重复的三元组。

**示例:**

输入: `[-1, 0, 1, 2, -1, -4]`

输出: `[[-1, 0, 1], [-1, -1, 2]]`

**说明:**
解决方案中不能包含重复的三元组。

#### 代码实现
```python
def three_sum(nums):
    res = []
    nums.sort()  # 先对数组进行排序，方便后续使用双指针查找三元组
    n = len(nums)
    
    # 遍历数组中的每个元素，作为三元组中的第一个元素
    for i in range(n - 2):
        # 跳过重复元素，避免结果中出现重复的三元组
        if i > 0 and nums[i] == nums[i - 1]:
            continue
        
        # 初始化双指针，left 指向当前元素的下一个位置，right 指向数组末尾
        left, right = i + 1, n - 1
        while left < right:
            # 计算三元组的和
            total = nums[i] + nums[left] + nums[right]
            if total == 0:
                # 如果和为 0，找到一个符合条件的三元组，添加到结果中
                res.append([nums[i], nums[left], nums[right]])
                # 跳过重复的左指针元素，避免重复三元组
                while left < right and nums[left] == nums[left + 1]:
                    left += 1
                # 跳过重复的右指针元素，避免重复三元组
                while left < right and nums[right] == nums[right - 1]:
                    right -= 1
                # 移动指针，寻找新的组合
                left += 1
                right -= 1
            elif total < 0:
                # 如果和小于 0，说明需要更大的值，将左指针右移
                left += 1
            else:
                # 如果和大于 0，说明需要更小的值，将右指针左移
                right -= 1
    
    return res

# 示例用法
nums = [-1, 0, 1, 2, -1, -4]
print(three_sum(nums))  # 输出: [[-1, -1, 2], [-1, 0, 1]]
```

#### 复杂度分析
- **时间复杂度**: O(n^2)，其中 n 是数组的长度。主要由双指针的遍历过程决定。
- **空间复杂度**: O(1)，不包括输出所需的空间，使用了常数级别的额外空间。

#### 总结
该算法首先对数组进行排序，使用双指针的方法来查找满足条件的三元组。通过跳过重复的元素来确保结果中不包含重复的三元组，时间复杂度为 O(n^2)。

#### 为什么要对数组进行排序
排序是为了方便使用双指针的方法来查找符合条件的三元组。在排序后的数组中，可以轻松地使用双指针（一个指向左侧，一个指向右侧）来缩小查找范围。

排序有以下几个好处：
1. **简化去重**：在遍历时，可以轻松跳过重复元素，避免产生重复的三元组。
2. **高效查找**：使用排序后的数组，可以通过左右双指针来有效地找到满足条件的三元组，从而将时间复杂度降低到 O(n^2)。如果数组未排序，则无法使用双指针，需要使用更多的嵌套循环，导致更高的时间复杂度。

#### 跳过重复元素的解释
在代码中，我们使用如下的方式跳过重复元素：

```python
if i > 0 and nums[i] == nums[i - 1]:
    continue
```

以及：

```python
while left < right and nums[left] == nums[left + 1]:
    left += 1
while left < right and nums[right] == nums[right - 1]:
    right -= 1
```

这些代码用于跳过重复的元素，确保结果中不包含重复的三元组。

1. **跳过重复的起始元素**：在外层循环中，`if i > 0 and nums[i] == nums[i - 1]` 用于跳过与前一个元素相同的值，因为以相同的值作为起点会得到相同的三元组，导致结果中出现重复。
2. **跳过重复的左、右指针元素**：在找到一个满足条件的三元组后，`while left < right and nums[left] == nums[left + 1]` 和 `while left < right and nums[right] == nums[right - 1]` 用于跳过左指针和右指针的重复元素。这样可以避免在结果中添加重复的三元组，同时将指针移动到下一个不同的元素位置，以继续查找新的组合。

这些跳过重复元素的操作是必要的，因为数组中可能包含多个相同的值，直接使用这些重复值会导致结果中出现重复的三元组。而通过这些判断和跳过操作，可以确保最终的结果集合中每个三元组都是唯一的。
