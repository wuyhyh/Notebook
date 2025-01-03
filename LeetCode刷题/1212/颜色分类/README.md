### **LeetCode 第75题 - 颜色分类**

#### **题目描述**
给定一个包含 `n` 个元素的数组，其中每个元素的值为 `0`、`1` 或 `2`，表示红色、白色和蓝色。需要对数组进行排序，使得相同颜色的元素相邻，并且按照红色、白色、蓝色的顺序排列。

**注意**：
- 不能使用库函数 `sort` 或 `sorted`，必须在 `O(n)` 时间复杂度和 **常数空间** 内完成排序。

---

### **解题思路**

本题可以使用 **荷兰国旗问题**（Dutch National Flag Problem）的解决方案，这是一种经典的三路快排思想。我们通过维护三个指针来划分三个区间，分别表示 `0`、`1` 和 `2` 的位置。

#### **三路快排法**
1. **初始化**三个指针：
    - `low`：指向当前处理区间的最左侧，表示红色区域（值为 `0`）。
    - `mid`：指向当前处理区间的中间，表示白色区域（值为 `1`）。
    - `high`：指向当前处理区间的最右侧，表示蓝色区域（值为 `2`）。

2. **操作步骤**：
    - 从左到右遍历数组，处理 `mid` 指向的元素：
        - 如果 `nums[mid] == 0`，将该元素与 `low` 指向的元素交换，并将 `low` 和 `mid` 向右移动一位。
        - 如果 `nums[mid] == 1`，说明它已经在正确的位置，直接将 `mid` 向右移动一位。
        - 如果 `nums[mid] == 2`，将该元素与 `high` 指向的元素交换，并将 `high` 向左移动一位，`mid` 不动，因为交换后的元素需要重新检查。

3. **结束条件**：
    - 当 `mid` 超过 `high` 时，排序完成。

---

### **代码实现**

```python
class Solution:
    def sortColors(self, nums):
        low, mid, high = 0, 0, len(nums) - 1
        
        while mid <= high:
            if nums[mid] == 0:
                # 交换 nums[mid] 和 nums[low]
                nums[low], nums[mid] = nums[mid], nums[low]
                low += 1
                mid += 1
            elif nums[mid] == 1:
                mid += 1
            else:
                # 交换 nums[mid] 和 nums[high]
                nums[high], nums[mid] = nums[mid], nums[high]
                high -= 1
                
```

---

### **代码解析**
- **指针初始化**：`low` 和 `mid` 都指向数组的开头，`high` 指向数组的最后一个元素。
- **遍历数组**：
    - 如果 `nums[mid] == 0`，则将 `nums[mid]` 和 `nums[low]` 交换，因为 `0` 应该放在左侧，然后 `low` 和 `mid` 向右移动。
    - 如果 `nums[mid] == 1`，不需要交换，直接将 `mid` 向右移动。
    - 如果 `nums[mid] == 2`，则将 `nums[mid]` 和 `nums[high]` 交换，然后将 `high` 向左移动，`mid` 不动，因为交换后的元素需要重新检查。
- **停止条件**：当 `mid` 指针超出 `high` 指针时，说明排序完成。

---

### **复杂度分析**
- **时间复杂度**：`O(n)`，其中 `n` 是数组的长度。我们仅需要遍历数组一次。
- **空间复杂度**：`O(1)`，我们只使用了常数级别的额外空间。

---

### **示例测试**

#### 示例 1：
```python
nums = [2, 0, 2, 1, 1, 0]
solution = Solution()
solution.sortColors(nums)
print(nums)  # 输出 [0, 0, 1, 1, 2, 2]
```

#### 示例 2：
```python
nums = [2, 0, 1]
solution = Solution()
solution.sortColors(nums)
print(nums)  # 输出 [0, 1, 2]
```

---

### **总结**
- 本题可以使用 **三路快排** 的思想解决，通过三个指针将数组分成三个部分：`0`、`1` 和 `2`，从而完成排序。
- 这种方法的优势在于 **O(n)** 的时间复杂度和 **O(1)** 的空间复杂度，十分高效。
