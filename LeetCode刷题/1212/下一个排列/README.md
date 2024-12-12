好的，我会根据你提供的内容整理一个文档，涵盖你提到的相关问题和解答。

---

# LeetCode题解文档

## 第31题 - 下一个排列 (Next Permutation)

### 题目描述
实现 `next permutation` 函数，计算给定数字序列的下一个排列（按字典序）。如果已经是最大的排列，返回最小的排列（即按升序排列）。

### 解题思路
- **关键步骤**：
    1. **从右向左找到第一个下降元素**：从右向左遍历，找到第一个元素 `nums[i]`，它小于 `nums[i+1]`。
    2. **找到比 `nums[i]` 大的最小元素**：从右向左再遍历，找到第一个比 `nums[i]` 大的元素 `nums[j]`，交换它们。
    3. **翻转后缀部分**：交换之后，后缀部分（即 `nums[i+1:]`）可能是递减的，翻转后缀部分，确保得到字典序最小的排列。

### 为什么要翻转后缀部分？
- **原因**：交换后，`nums[i+1:]` 部分会是递减的。为了保证我们得到下一个最小的字典序排列，需要将该部分翻转成递增的顺序。这样可以确保最后的排列是字典序中的下一个排列，而不是更大的排列。

### 代码实现

```python
class Solution:
    def nextPermutation(self, nums):
        # Step 1: Find the first decreasing element from the right
        i = len(nums) - 2
        while i >= 0 and nums[i] >= nums[i + 1]:
            i -= 1
        
        # Step 2: If there is a decreasing element, find the element to swap with
        if i >= 0:
            j = len(nums) - 1
            while nums[j] <= nums[i]:
                j -= 1
            # Step 3: Swap nums[i] and nums[j]
            nums[i], nums[j] = nums[j], nums[i]
        
        # Step 4: Reverse the elements after index i
        nums[i + 1:] = reversed(nums[i + 1:])
```

### 代码解析
- **步骤1**：从右向左找到第一个下降元素 `nums[i]`。
- **步骤2**：从右向左找到第一个比 `nums[i]` 大的元素 `nums[j]`，并交换它们。
- **步骤3**：交换后，后面的部分（`nums[i+1:]`）是递减的，需要翻转该部分，以得到下一个最小字典序的排列。
- **时间复杂度**：`O(n)`，我们进行了两次遍历和一次翻转操作。
- **空间复杂度**：`O(1)`，我们只使用了常数空间。

---

## 第136题 - 只出现一次的数字 (Single Number)

### 题目描述
给定一个非空整数数组 `nums`，其中除了一个元素只出现一次外，其余每个元素都出现两次。请你找出那个只出现一次的元素。

### 解题思路
我们可以利用**异或运算**（XOR）来解决这个问题，利用以下异或的性质：
1. `a ^ a = 0`，即任何数与自己异或结果为0。
2. `a ^ 0 = a`，即任何数与0异或结果为它本身。
3. 异或运算是交换和结合的。

通过异或所有的元素，成对的元素会相互抵消，最终剩下的就是只出现一次的元素。

### 代码实现

```python
class Solution:
    def singleNumber(self, nums):
        result = 0
        for num in nums:
            result ^= num  # 对每个数进行异或
        return result
```

### 代码解析
1. 初始化 `result = 0`。
2. 遍历数组，每次对 `result` 和当前元素 `num` 进行异或操作。
3. 最终，`result` 中的值就是那个只出现一次的数字。

### 复杂度分析
- **时间复杂度**：`O(n)`，其中 `n` 是数组的长度。只需要遍历一次数组。
- **空间复杂度**：`O(1)`，只使用了一个额外的变量。

---

## 第75题 - 颜色分类 (Sort Colors)

### 题目描述
给定一个包含 `n` 个元素的数组，其中每个元素的值为 `0`、`1` 或 `2`，表示红色、白色和蓝色。需要对数组进行排序，使得相同颜色的元素相邻，并且按照红色、白色、蓝色的顺序排列。

### 解题思路
使用**荷兰国旗问题**的解决方案。通过三个指针来划分三个区间，分别表示 `0`、`1` 和 `2` 的位置。
- `low`：指向红色区域（值为 `0`）。
- `mid`：指向白色区域（值为 `1`）。
- `high`：指向蓝色区域（值为 `2`）。

遍历数组，根据当前 `mid` 指向的元素进行相应的交换，确保最终数组按字典序排序。

### 代码实现

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

### 代码解析
1. **指针初始化**：`low` 和 `mid` 都指向数组的开头，`high` 指向数组的最后一个元素。
2. **遍历数组**：
    - 如果 `nums[mid] == 0`，则将 `nums[mid]` 和 `nums[low]` 交换，`low` 和 `mid` 向右移动。
    - 如果 `nums[mid] == 1`，不需要交换，直接将 `mid` 向右移动。
    - 如果 `nums[mid] == 2`，则将 `nums[mid]` 和 `nums[high]` 交换，`high` 向左移动，`mid` 不动。
3. **停止条件**：当 `mid` 超过 `high` 时，排序完成。

### 复杂度分析
- **时间复杂度**：`O(n)`，只遍历一次数组。
- **空间复杂度**：`O(1)`，只使用了常数级别的额外空间。

---

## 总结
通过这些题目，我们学到了如何使用常见的算法技巧来解决不同类型的排序和查找问题：
- **异或运算**：解决只出现一次的数字问题。
- **荷兰国旗问题**：通过三指针排序数组。
- **下一个排列**：通过字典序的算法生成下一个排列。
