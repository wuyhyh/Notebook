LeetCode 第4题是 **寻找两个正序数组的中位数**，该问题的描述如下：

### 题目描述

给定两个大小分别为 `m` 和 `n` 的正序数组 `nums1` 和 `nums2`。请你找出这两个正序数组的中位数，并且要求算法的时间复杂度为 `O(log(min(m, n)))`。

你可以假设 `nums1` 和 `nums2` 不为空。

### 示例 1

```plaintext
输入: nums1 = [1, 3], nums2 = [2]
输出: 2.0
解释: 合并数组 = [1, 2, 3]，中位数 2 位于中间。
```

### 示例 2

```plaintext
输入: nums1 = [1, 2], nums2 = [3, 4]
输出: 2.5
解释: 合并数组 = [1, 2, 3, 4]，中位数是 (2 + 3) / 2 = 2.5。
```

### 解题思路

为了达到时间复杂度 `O(log(min(m, n)))`，我们不能使用常规的合并排序算法，因为那样的时间复杂度是 `O(m + n)`，而是应该利用二分查找的思想来解决这个问题。核心思想是使用二分查找将两个数组分割成左右两部分，使得左部分的所有元素都小于右部分的所有元素。

### 详细步骤：

1. **目标**：我们需要找出合并后的数组的中位数。中位数是：
    - 如果总元素个数是奇数，则中位数是合并后数组的中间元素。
    - 如果总元素个数是偶数，则中位数是中间两个元素的平均值。

2. **分割数组**：
    - 假设我们将两个数组分成左半部分和右半部分，使得左半部分的元素个数等于右半部分的元素个数，或者左半部分比右半部分多一个元素（当总元素个数为奇数时）。
    - 我们通过二分查找来选择一个合适的位置将 `nums1` 和 `nums2` 分割开，使得左部分的最大值小于右部分的最小值。

3. **二分查找过程**：
    - 在较小的数组上进行二分查找，将其分成左半部分和右半部分。通过调整分割的位置，确保：
        - 左部分的最大值小于右部分的最小值。
    - 一旦分割合适，我们就能计算中位数。

### 代码实现

```python
def findMedianSortedArrays(nums1, nums2):
    # 确保 nums1 是较小的数组，这样我们在 nums1 上做二分查找
    if len(nums1) > len(nums2):
        nums1, nums2 = nums2, nums1

    m, n = len(nums1), len(nums2)
    left, right = 0, m
    median = 0.0

    while left <= right:
        # 在 nums1 上进行二分查找
        partition1 = (left + right) // 2
        partition2 = (m + n + 1) // 2 - partition1

        # 获取 nums1 和 nums2 的左右部分的最大最小值
        maxLeft1 = float('-inf') if partition1 == 0 else nums1[partition1 - 1]
        minRight1 = float('inf') if partition1 == m else nums1[partition1]

        maxLeft2 = float('-inf') if partition2 == 0 else nums2[partition2 - 1]
        minRight2 = float('inf') if partition2 == n else nums2[partition2]

        # 检查是否满足条件
        if maxLeft1 <= minRight2 and maxLeft2 <= minRight1:
            # 如果总长度是偶数
            if (m + n) % 2 == 0:
                median = (max(maxLeft1, maxLeft2) + min(minRight1, minRight2)) / 2
            else:
                median = max(maxLeft1, maxLeft2)
            return median
        elif maxLeft1 > minRight2:
            right = partition1 - 1
        else:
            left = partition1 + 1

    raise ValueError("Input arrays are not sorted.")
```

### 代码解析

1. **交换数组**：我们首先确保 `nums1` 是较小的数组，这样可以减少二分查找的范围，提高效率。

2. **二分查找**：
    - 我们在 `nums1` 上进行二分查找，计算出 `partition1`，然后根据 `partition1` 计算出 `partition2`（`partition2` 是 `nums2` 数组的分割位置）。
    - `partition1` 和 `partition2` 保证了左半部分的元素个数和右半部分的元素个数接近或相等。

3. **计算最大最小值**：
    - `maxLeft1` 和 `minRight1` 分别是 `nums1` 左半部分的最大值和右半部分的最小值。
    - `maxLeft2` 和 `minRight2` 分别是 `nums2` 左半部分的最大值和右半部分的最小值。
    - 如果 `partition1 == 0` 或 `partition2 == 0`，表示没有左半部分或右半部分，此时赋予负无穷和正无穷。

4. **检查条件**：我们检查是否满足：
    - `maxLeft1 <= minRight2` 和 `maxLeft2 <= minRight1`，如果满足则找到了合适的分割点。

5. **返回中位数**：
    - 如果总长度是偶数，则中位数是左半部分最大值和右半部分最小值的平均值。
    - 如果总长度是奇数，则中位数是左半部分的最大值。

6. **调整查找区间**：如果左部分的最大值大于右部分的最小值，则说明 `partition1` 太大，调整查找区间；否则，调整为更大的 `partition1`。

### 时间复杂度

- **时间复杂度**：`O(log(min(m, n)))`。由于我们在较小的数组上进行二分查找，每次查找都将范围缩小一半。

- **空间复杂度**：`O(1)`。只使用了常数空间来存储分割的索引和边界值。

### 示例解析

#### 示例 1：

```python
print(findMedianSortedArrays([1, 3], [2]))
```

输出：

```plaintext
2.0
```

- 合并数组：[1, 2, 3]，中位数是 2。

#### 示例 2：

```python
print(findMedianSortedArrays([1, 2], [3, 4]))
```

输出：

```plaintext
2.5
```

- 合并数组：[1, 2, 3, 4]，中位数是 (2 + 3) / 2 = 2.5。

### 总结

| 方法       | 时间复杂度     | 空间复杂度     | 适用场景              |
|------------|----------------|----------------|-----------------------|
| 二分查找法 | `O(log(min(m, n)))` | `O(1)`          | 适用于两个有序数组求中位数的问题 |

这种方法通过二分查找实现了时间复杂度 `O(log(min(m, n)))`，显著提高了效率。
