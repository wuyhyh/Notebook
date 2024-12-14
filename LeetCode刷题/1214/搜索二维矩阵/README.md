### **LeetCode 第74题 - 搜索二维矩阵 (Search a 2D Matrix)**

#### **题目描述**
编写一个高效的算法来查找一个二维矩阵中的目标值 `target`。该矩阵具有以下特性：
1. 每行的元素从左到右按升序排列。
2. 每列的元素从上到下按升序排列。

**要求**：
- 设计一个时间复杂度为 `O(log(m * n))` 的算法，其中 `m` 和 `n` 分别是矩阵的行数和列数。

---

### **解题思路**

给定矩阵的特性，首先可以将二维矩阵视为一个一维的有序数组。由于矩阵中的每一行和每一列都是升序排列的，因此可以使用 **二分查找** 来高效地找到目标值。

#### **步骤**：
1. **将矩阵视为一维数组**：
    - 给定矩阵 `matrix` 有 `m` 行和 `n` 列，每行有 `n` 个元素。
    - 我们可以将二维矩阵的元素映射到一维数组中，位置 `(i, j)` 的元素可以通过公式 `index = i * n + j` 映射到一维数组的下标。这个映射是线性的，保证了从左到右、从上到下的顺序。

2. **二分查找**：
    - 我们将矩阵视为一个大小为 `m * n` 的有序数组，使用二分查找查找目标元素。
    - **二分查找的原理**：
        - 计算中间元素的位置：`mid = (left + right) // 2`。
        - 使用映射公式将一维数组的索引映射回二维数组的行列位置：
            - 行：`row = mid // n`。
            - 列：`col = mid % n`。
        - 比较 `matrix[row][col]` 与 `target` 的大小关系，根据结果调整查找区间。

#### **时间复杂度**：
- 二分查找的时间复杂度是 `O(log(m * n))`，因此满足题目要求。

---

### **代码实现**

```python
class Solution:
    def searchMatrix(self, matrix: list[list[int]], target: int) -> bool:
        if not matrix or not matrix[0]:
            return False
        
        m, n = len(matrix), len(matrix[0])
        left, right = 0, m * n - 1
        
        while left <= right:
            mid = (left + right) // 2
            # 将一维索引 mid 映射到二维数组中的行列位置
            row, col = mid // n, mid % n
            if matrix[row][col] == target:
                return True
            elif matrix[row][col] < target:
                left = mid + 1
            else:
                right = mid - 1
        
        return False
```

### **代码解析**
1. **初始化**：
    - `m` 为矩阵的行数，`n` 为矩阵的列数，`left` 和 `right` 分别为二分查找的左右边界。

2. **映射关系**：
    - 通过 `mid // n` 计算行索引，通过 `mid % n` 计算列索引。这样就能够将一维索引 `mid` 映射到二维矩阵的 `(row, col)`。

3. **二分查找**：
    - 通过 `matrix[row][col]` 与 `target` 的比较来决定更新左右边界。
    - 如果 `matrix[row][col] == target`，返回 `True`。
    - 如果 `matrix[row][col] < target`，说明目标值在右侧，更新 `left`。
    - 如果 `matrix[row][col] > target`，说明目标值在左侧，更新 `right`。

4. **返回结果**：
    - 如果二分查找结束后没有找到目标值，返回 `False`。

---

### **时间复杂度**
- **时间复杂度**：`O(log(m * n))`，每次二分查找将搜索空间缩小一半。
- **空间复杂度**：`O(1)`，我们只用了常数空间。

---

### **示例测试**

#### 示例 1：
```python
matrix = [
  [1, 4, 7, 11],
  [2, 5, 8, 12],
  [3, 6, 9, 16],
  [10, 13, 14, 17]
]
target = 5
solution = Solution()
print(solution.searchMatrix(matrix, target))  # 输出 True
```

**解释**：
- 目标 `5` 存在于矩阵中，位于 `(1, 1)` 位置。

#### 示例 2：
```python
matrix = [
  [1, 4, 7, 11],
  [2, 5, 8, 12],
  [3, 6, 9, 16],
  [10, 13, 14, 17]
]
target = 20
solution = Solution()
print(solution.searchMatrix(matrix, target))  # 输出 False
```

**解释**：
- 目标 `20` 不存在于矩阵中，返回 `False`。

---

### **总结**
- 本题通过将二维矩阵视为一维有序数组，使用 **二分查找** 来高效地找到目标值。
- **二分查找** 的时间复杂度为 `O(log(m * n))`，符合题目要求的时间复杂度。
- 通过简单的映射公式，我们将二分查找扩展到二维矩阵中，解决了这个问题。
