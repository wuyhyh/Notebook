好的，下面是整理好的文档，详细讲解了第54题“螺旋矩阵”以及 `while` 循环条件和遍历下边界、左边界时的 `if` 判断。

---

# LeetCode 54. 螺旋矩阵（Spiral Matrix）

## 问题描述

给定一个 `m x n` 的矩阵，按顺时针的螺旋顺序返回矩阵中的所有元素。

### 示例

**示例 1:**

输入：
```plaintext
[
 [ 1, 2, 3 ],
 [ 4, 5, 6 ],
 [ 7, 8, 9 ]
]
```

输出：
```plaintext
[1, 2, 3, 6, 9, 8, 7, 4, 5]
```

**示例 2:**

输入：
```plaintext
[
 [1, 2, 3, 4],
 [5, 6, 7, 8],
 [9, 10, 11, 12]
]
```

输出：
```plaintext
[1, 2, 3, 4, 8, 12, 11, 10, 9, 5, 6, 7]
```

## 解题思路

### 螺旋顺序遍历
我们通过维护四个边界（`top`、`bottom`、`left`、`right`）来模拟矩阵的螺旋遍历。每遍历一圈后，我们更新这些边界，逐步缩小待遍历的矩阵区域。

1. **初始化四个边界**：
    - `top` = 0
    - `bottom` = m - 1
    - `left` = 0
    - `right` = n - 1

2. **遍历矩阵**：  
   在每一圈的遍历中：
    - 从`left`到`right`遍历上边界。
    - 从`top`到`bottom`遍历右边界。
    - 从`right`到`left`遍历下边界（需加`if`判断）。
    - 从`bottom`到`top`遍历左边界（需加`if`判断）。

   每次完成一圈后，更新边界，直到所有元素都被遍历。

### 代码实现：

```python
def spiralOrder(matrix):
    # 如果矩阵为空，直接返回空列表
    if not matrix:
        return []
    
    result = []
    
    top, bottom, left, right = 0, len(matrix) - 1, 0, len(matrix[0]) - 1
    
    while top <= bottom and left <= right:
        # 遍历上边界
        for i in range(left, right + 1):
            result.append(matrix[top][i])
        top += 1
        
        # 遍历右边界
        for i in range(top, bottom + 1):
            result.append(matrix[i][right])
        right -= 1
        
        # 遍历下边界，必须判断 top <= bottom，避免重复遍历已遍历的行
        if top <= bottom:
            for i in range(right, left - 1, -1):
                result.append(matrix[bottom][i])
            bottom -= 1
        
        # 遍历左边界，必须判断 left <= right，避免重复遍历已遍历的列
        if left <= right:
            for i in range(bottom, top - 1, -1):
                result.append(matrix[i][left])
            left += 1
    
    return result
```

### 代码解释

1. **初始化边界**：
    - `top`、`bottom`、`left` 和 `right` 分别表示当前有效矩阵区域的上下左右边界。

2. **`while` 循环条件**：
    - `while top <= bottom and left <= right`，表示矩阵中仍然有未遍历的部分。如果所有有效区域都已遍历完，循环将停止。

3. **遍历顺序**：
    - **上边界**：从 `left` 到 `right` 遍历当前的 `top` 行，遍历完后 `top += 1`。
    - **右边界**：从 `top` 到 `bottom` 遍历当前的 `right` 列，遍历完后 `right -= 1`。
    - **下边界**：从 `right` 到 `left` 遍历当前的 `bottom` 行，遍历完后 `bottom -= 1`。
    - **左边界**：从 `bottom` 到 `top` 遍历当前的 `left` 列，遍历完后 `left += 1`。

4. **`if` 判断**：
    - **下边界的 `if` 判断**：
      ```python
      if top <= bottom:
          for i in range(right, left - 1, -1):
              result.append(matrix[bottom][i])
          bottom -= 1
      ```
      只有当 `top <= bottom` 时，说明下边界的行还没有被遍历，才需要遍历下边界。

    - **左边界的 `if` 判断**：
      ```python
      if left <= right:
          for i in range(bottom, top - 1, -1):
              result.append(matrix[i][left])
          left += 1
      ```
      只有当 `left <= right` 时，说明左边界的列还没有被遍历，才需要遍历左边界。

### 时间复杂度和空间复杂度分析

- **时间复杂度**：`O(m * n)`，其中 `m` 是矩阵的行数，`n` 是矩阵的列数。我们需要遍历矩阵中的每个元素一次。
- **空间复杂度**：`O(1)`，除了存储结果的列表 `result`，我们只用了常数的空间来保存边界值。

## 总结

- 通过调整 `top`、`bottom`、`left` 和 `right` 四个边界来模拟矩阵的螺旋顺序遍历。
- 遍历下边界和左边界时，需要使用 `if` 判断，以避免重复遍历已经遍历过的行或列。
- 这种方法的时间和空间复杂度都非常高效。

---

如果你对这个解法或代码有任何疑问，随时可以向我提问！
