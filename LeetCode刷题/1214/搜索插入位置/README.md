### **LeetCode 第35题 - 搜索插入位置 (Search Insert Position)**

#### **题目描述**
给定一个排序数组 `nums` 和一个目标值 `target`，返回 `target` 应该被插入的位置，使得 `nums` 仍然保持排序。

**要求**：
- 你必须实现时间复杂度为 `O(log n)` 的算法。

---

### **解题思路**

这个问题的核心是找到一个可以插入 `target` 的位置，保持数组的排序。因为数组是排序的，我们可以使用 **二分查找**（Binary Search）来高效地找到该位置。这样可以将时间复杂度从 `O(n)` 降到 `O(log n)`。

#### **二分查找的关键思想**：
1. 如果 `target` 存在于数组中，返回它的索引。
2. 如果 `target` 不存在于数组中，返回它应该插入的位置。

#### **二分查找的流程**：
1. 设置两个指针 `left` 和 `right`，分别指向数组的开始和结束。
2. 计算中间位置 `mid`。
3. 如果 `nums[mid]` 等于 `target`，返回 `mid`。
4. 如果 `nums[mid]` 小于 `target`，说明 `target` 应该在右半部分，更新 `left` 为 `mid + 1`。
5. 如果 `nums[mid]` 大于 `target`，说明 `target` 应该在左半部分，更新 `right` 为 `mid - 1`。
6. 当 `left` 超过 `right` 时，`target` 没有找到，`left` 就是应该插入的位置。

#### **插入位置**：
- 如果遍历结束时，`left` 位置就是目标元素 `target` 应插入的索引位置。

---

### **代码实现**

```python
class Solution:
    def searchInsert(self, nums: list[int], target: int) -> int:
        left, right = 0, len(nums) - 1
        
        while left <= right:
            mid = (left + right) // 2
            
            if nums[mid] == target:
                return mid
            elif nums[mid] < target:
                left = mid + 1
            else:
                right = mid - 1
        
        return left  # 如果没找到 target，left 即为插入位置
```

### **代码解析**
1. **初始化**：我们定义两个指针 `left` 和 `right`，分别指向数组的开头和结尾。
2. **循环**：每次通过计算中间值 `mid`，根据 `nums[mid]` 和 `target` 的大小关系调整左右指针的位置，逐步缩小查找范围。
3. **插入位置**：如果在数组中找到了 `target`，返回 `mid`；如果没有找到，返回 `left`，即插入 `target` 时的位置。

---

### **时间复杂度**
- **时间复杂度**：`O(log n)`，每次二分查找都会将查找区间减半。
- **空间复杂度**：`O(1)`，我们只用了常数空间。

---

### **示例测试**

#### 示例 1：
```python
nums = [1, 3, 5, 6]
target = 5
solution = Solution()
print(solution.searchInsert(nums, target))  # 输出 2
```

**解释**：`5` 在数组中的索引位置是 `2`，因此返回 `2`。

#### 示例 2：
```python
nums = [1, 3, 5, 6]
target = 2
solution = Solution()
print(solution.searchInsert(nums, target))  # 输出 1
```

**解释**：`2` 不在数组中，但应该插入到索引 `1` 位置，使得数组仍然保持排序。

#### 示例 3：
```python
nums = [1, 3, 5, 6]
target = 7
solution = Solution()
print(solution.searchInsert(nums, target))  # 输出 4
```

**解释**：`7` 不在数组中，应该插入到数组的最后位置，即索引 `4`。

---

### **总结**
- 本题要求在排序数组中找到一个元素的插入位置，可以利用 **二分查找** 提高效率，达到 `O(log n)` 的时间复杂度。
- 关键在于理解二分查找的原理，通过比较 `mid` 和 `target` 来调整查找区间，并最终返回插入位置。
