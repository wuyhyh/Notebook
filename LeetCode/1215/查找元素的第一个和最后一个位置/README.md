### **LeetCode 第34题 - 在排序数组中查找元素的第一个和最后一个位置 (Find First and Last Position of Element in Sorted Array)**

#### **题目描述**
给定一个按非降序排列的整数数组 `nums` 和一个目标值 `target`，请你在数组中查找 `target` 的第一个和最后一个位置。如果目标值不存在于数组中，返回 `[-1, -1]`。

**要求：**
- 你必须设计一个时间复杂度为 `O(log n)` 的算法。

---

### **解题思路**

由于题目要求时间复杂度为 `O(log n)`，这意味着我们必须使用 **二分查找** 来解决这个问题。利用二分查找可以在 `O(log n)` 时间内查找目标值的第一个和最后一个位置。

#### **步骤**：
1. **查找第一个位置**：我们可以通过修改传统的二分查找来找到目标值的第一个位置。如果中间值等于目标值，继续向左搜索，直到找到第一个匹配的位置。
2. **查找最后一个位置**：类似地，我们可以通过修改二分查找找到目标值的最后一个位置。如果中间值等于目标值，继续向右搜索，直到找到最后一个匹配的位置。

具体做法是，使用两个单独的二分查找来分别寻找第一个和最后一个位置。

### **代码实现**

```python
class Solution:
    def searchRange(self, nums: list[int], target: int) -> list[int]:
        # 查找第一个位置的二分查找
        def find_first():
            left, right = 0, len(nums) - 1
            while left <= right:
                mid = (left + right) // 2
                if nums[mid] < target:
                    left = mid + 1
                elif nums[mid] > target:
                    right = mid - 1
                else:
                    if mid == 0 or nums[mid - 1] != target:
                        return mid
                    right = mid - 1
            return -1

        # 查找最后一个位置的二分查找
        def find_last():
            left, right = 0, len(nums) - 1
            while left <= right:
                mid = (left + right) // 2
                if nums[mid] < target:
                    left = mid + 1
                elif nums[mid] > target:
                    right = mid - 1
                else:
                    if mid == len(nums) - 1 or nums[mid + 1] != target:
                        return mid
                    left = mid + 1
            return -1

        # 查找第一个和最后一个位置
        first = find_first()
        if first == -1:
            return [-1, -1]
        last = find_last()
        return [first, last]
```

### **代码解析**
1. **find_first 函数**：
    - 该函数用来查找目标值的第一个位置。
    - 如果 `nums[mid]` 等于目标值，我们进一步检查左侧的元素（`mid - 1`）是否也是目标值，直到找到第一个目标值。

2. **find_last 函数**：
    - 该函数用来查找目标值的最后一个位置。
    - 如果 `nums[mid]` 等于目标值，我们进一步检查右侧的元素（`mid + 1`）是否也是目标值，直到找到最后一个目标值。

3. **主函数 searchRange**：
    - 首先调用 `find_first()` 查找目标值的第一个位置，如果没有找到则返回 `[-1, -1]`。
    - 如果找到第一个位置，则调用 `find_last()` 查找目标值的最后一个位置。
    - 返回第一个和最后一个位置的数组。

### **时间复杂度**
- **时间复杂度**：`O(log n)`，因为我们只进行了两次二分查找，每次查找的时间复杂度是 `O(log n)`。
- **空间复杂度**：`O(1)`，只使用了常数空间。

### **示例测试**

#### 示例 1：
```python
nums = [5, 7, 7, 8, 8, 10]
target = 8
solution = Solution()
print(solution.searchRange(nums, target))  # 输出 [3, 4]
```

**解释**：
- 数组中的第一个 `8` 的索引是 `3`，最后一个 `8` 的索引是 `4`。

#### 示例 2：
```python
nums = [5, 7, 7, 8, 8, 10]
target = 6
solution = Solution()
print(solution.searchRange(nums, target))  # 输出 [-1, -1]
```

**解释**：
- 数组中没有 `6`，所以返回 `[-1, -1]`。

#### 示例 3：
```python
nums = []
target = 0
solution = Solution()
print(solution.searchRange(nums, target))  # 输出 [-1, -1]
```

**解释**：
- 数组为空，返回 `[-1, -1]`。

---

### **总结**

- **二分查找**是解决此题的关键，利用两次二分查找可以在 `O(log n)` 时间内找到目标值的第一个和最后一个位置。
- 由于题目要求时间复杂度为 `O(log n)`，因此使用二分查找是最优的解法。
- 通过两次查找（分别查找第一个和最后一个位置），我们可以有效地解决这个问题。
