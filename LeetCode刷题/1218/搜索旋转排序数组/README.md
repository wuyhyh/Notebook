LeetCode第33题是《搜索旋转排序数组》（Search in Rotated Sorted Array），题目要求在一个经过旋转的升序数组中找到目标值 `target` 的索引。如果目标值不存在，返回 `-1`。

### 题目描述
给定一个整数数组 `nums`，其中元素已经按升序排列，然后将数组的一部分旋转。旋转后的数组可能是升序的，也可能是部分升序的。你需要在这个旋转排序数组中查找目标值 `target`，如果找到，返回其索引；否则返回 `-1`。

### 示例
```plaintext
输入: nums = [4,5,6,7,0,1,2], target = 0
输出: 4
```

```plaintext
输入: nums = [4,5,6,7,0,1,2], target = 3
输出: -1
```

### 解题思路

这个问题的核心是利用旋转排序数组的特点，可以使用二分查找来提高搜索效率。旋转排序数组的一个关键特征是：在数组的一部分中，元素依然是有序的，另一部分也仍然是有序的。

通过二分查找，可以将问题分成两部分：
1. 确定中点 `mid` 的位置。
2. 判断哪一部分是有序的，进而决定应该向哪个方向查找。

### 步骤
1. **初始化指针**：
    - `left = 0`
    - `right = len(nums) - 1`

2. **进行二分查找**：
    - 计算 `mid = (left + right) // 2`。
    - 判断 `nums[mid]` 是否等于 `target`，如果相等，返回 `mid`。
    - 判断哪一半是有序的：
        - 如果 `nums[left] <= nums[mid]`，说明左边是有序的。
        - 如果 `nums[mid] <= nums[right]`，说明右边是有序的。

3. **决定搜索的方向**：
    - 如果左半部分有序，且 `target` 在 `nums[left]` 和 `nums[mid]` 之间，更新 `right = mid - 1`，继续在左半部分查找。
    - 如果右半部分有序，且 `target` 在 `nums[mid]` 和 `nums[right]` 之间，更新 `left = mid + 1`，继续在右半部分查找。

4. **返回结果**：
    - 如果没有找到 `target`，返回 `-1`。

### 代码实现（Python）
```python
def search(nums, target):
    left, right = 0, len(nums) - 1
    
    while left <= right:
        mid = (left + right) // 2
        
        if nums[mid] == target:  # 找到目标
            return mid
        
        # 判断哪一部分是有序的
        if nums[left] <= nums[mid]:
            # 左边有序
            if nums[left] <= target < nums[mid]:
                right = mid - 1  # target在左边
            else:
                left = mid + 1  # target在右边
        else:
            # 右边有序
            if nums[mid] < target <= nums[right]:
                left = mid + 1  # target在右边
            else:
                right = mid - 1  # target在左边
    
    return -1  # 未找到目标
```

### 时间复杂度
- 时间复杂度是 `O(log n)`，因为我们每次都将搜索范围缩小一半。

### 空间复杂度
- 空间复杂度是 `O(1)`，只使用了常数空间。

### 例子解析

以 `nums = [4, 5, 6, 7, 0, 1, 2]` 和 `target = 0` 为例：

1. **第一次迭代**：
    - `left = 0`, `right = 6`, `mid = 3`, `nums[mid] = 7`。
    - `nums[left] = 4 <= nums[mid] = 7`，说明左边有序。
    - `target = 0` 不在左边有序区间 `[4, 7]` 内，更新 `left = mid + 1 = 4`。

2. **第二次迭代**：
    - `left = 4`, `right = 6`, `mid = 5`, `nums[mid] = 1`。
    - `nums[left] = 0 <= nums[mid] = 1`，左边有序。
    - `target = 0` 在左边有序区间 `[0, 1]` 内，更新 `right = mid - 1 = 4`。

3. **第三次迭代**：
    - `left = 4`, `right = 4`, `mid = 4`, `nums[mid] = 0`。
    - 找到目标值 `0`，返回索引 `4`。

最终返回 `4`。

---

这个解法利用了旋转排序数组的特点，通过二分查找的方式将时间复杂度降到了 `O(log n)`，显著提升了搜索效率。
