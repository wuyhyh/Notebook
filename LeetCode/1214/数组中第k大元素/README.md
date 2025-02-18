### **LeetCode 第215题 - 数组中的第K个最大元素 (Kth Largest Element in an Array)**

#### **题目描述**
给定一个整数数组 `nums` 和一个整数 `k`，请你找出数组中第 `k` 个最大的元素。

**要求**：
- 你必须设计一个时间复杂度为 `O(n log k)` 或更优的算法。

---

### **解题思路**

这个问题可以通过以下几种方式来解决：

#### **思路一：排序法（简单直接）**
1. 我们可以先将数组 `nums` 排序，然后返回排序后的第 `k` 个元素。
2. 排序后，第 `k` 个最大的元素的索引为 `len(nums) - k`。

- **时间复杂度**：`O(n log n)`，排序操作的时间复杂度是 `O(n log n)`。
- **空间复杂度**：`O(1)`（如果原地排序的话）或 `O(n)`（如果使用了额外的排序空间）。

这种方法虽然简单，但并不符合题目对时间复杂度的要求，因为它的时间复杂度是 `O(n log n)`，对于大数组可能不是最佳选择。

#### **思路二：堆法（优于排序法）**
我们可以利用最小堆来高效地解决这个问题。
- 维护一个大小为 `k` 的最小堆，堆顶存储的是堆中最小的元素。
- 遍历数组中的元素，每次将元素加入堆中。如果堆的大小超过 `k`，则删除堆顶元素。
- 最终，堆顶元素就是第 `k` 个最大的元素。

**堆的操作**：插入元素和删除堆顶元素的时间复杂度都是 `O(log k)`，因此总的时间复杂度是 `O(n log k)`。

- **时间复杂度**：`O(n log k)`，插入 `n` 个元素，每个插入操作的时间复杂度为 `O(log k)`。
- **空间复杂度**：`O(k)`，堆的大小为 `k`。

#### **思路三：快速选择算法（QuickSelect）**
快速选择是一种基于快速排序的算法，它可以在平均 `O(n)` 的时间内找到第 `k` 个最大元素。其核心思想是利用快速排序的分治思想，通过选取一个随机的 `pivot`，将数组分成两个部分，然后递归地选择合适的部分。

- **时间复杂度**：
    - 最优情况下是 `O(n)`（当每次都选到合适的 pivot）。
    - 最坏情况下是 `O(n^2)`（当每次选到的 pivot 都是极端的元素）。
- **空间复杂度**：`O(1)`（不需要额外的空间，只使用原数组）。

---

### **代码实现：堆法**

下面我们使用堆来解决这个问题，堆法的时间复杂度为 `O(n log k)`。

```python
import heapq

class Solution:
    def findKthLargest(self, nums: list[int], k: int) -> int:
        # 使用最小堆，堆的大小为 k
        min_heap = []
        
        # 遍历数组中的每个数
        for num in nums:
            # 将当前数加入堆
            heapq.heappush(min_heap, num)
            # 如果堆的大小超过 k，弹出堆顶元素
            if len(min_heap) > k:
                heapq.heappop(min_heap)
        
        # 堆顶元素即为第 k 个最大的元素
        return min_heap[0]
```

### **代码解析**
1. **最小堆**：
    - 使用 Python 内置的 `heapq` 库来实现堆。
    - `heapq.heappush(min_heap, num)` 将 `num` 添加到堆中。
    - `heapq.heappop(min_heap)` 删除堆顶元素，这样可以确保堆中最多只保留 `k` 个元素。

2. **堆的大小**：
    - 每次向堆中添加元素后，如果堆的大小超过了 `k`，则删除堆顶元素，确保堆中只有 `k` 个元素，且这些元素是数组中最大的 `k` 个元素。

3. **返回结果**：
    - 当遍历完数组后，堆中剩下的是数组中最大的 `k` 个元素，堆顶元素即为第 `k` 个最大的元素。

---

### **代码实现：快速选择法（QuickSelect）**

快速选择法的实现更加复杂，但它能提供更优的平均时间复杂度。以下是该算法的实现：

```python
import random

class Solution:
    def findKthLargest(self, nums: list[int], k: int) -> int:
        def quickselect(left, right):
            pivot = random.randint(left, right)
            nums[pivot], nums[right] = nums[right], nums[pivot]
            pivot_index = left
            for i in range(left, right):
                if nums[i] < nums[right]:
                    nums[i], nums[pivot_index] = nums[pivot_index], nums[i]
                    pivot_index += 1
            nums[pivot_index], nums[right] = nums[right], nums[pivot_index]
            
            if pivot_index == len(nums) - k:
                return nums[pivot_index]
            elif pivot_index < len(nums) - k:
                return quickselect(pivot_index + 1, right)
            else:
                return quickselect(left, pivot_index - 1)

        return quickselect(0, len(nums) - 1)
```

### **代码解析**
1. **分区操作**：
    - 我们使用 `random.randint` 随机选择一个 `pivot`，并通过交换使得 `pivot` 作为分隔元素。
    - 之后将数组按元素是否小于 `pivot` 进行划分。

2. **递归选择**：
    - 如果 `pivot_index` 恰好是 `len(nums) - k`，则表示我们找到了第 `k` 个最大元素。
    - 如果 `pivot_index` 小于 `len(nums) - k`，说明第 `k` 个最大元素在右边，递归选择右半部分。
    - 如果 `pivot_index` 大于 `len(nums) - k`，说明第 `k` 个最大元素在左边，递归选择左半部分。

---

### **时间复杂度**
- **堆法**：`O(n log k)`，因为每次插入堆的时间复杂度是 `O(log k)`，我们总共要进行 `n` 次插入操作。
- **快速选择法**：平均情况下 `O(n)`，最坏情况下 `O(n^2)`。

---

### **示例测试**

#### 示例 1：
```python
nums = [3, 2, 1, 5, 6, 4]
k = 2
solution = Solution()
print(solution.findKthLargest(nums, k))  # 输出 5
```

**解释**：数组中第二大的元素是 `5`。

#### 示例 2：
```python
nums = [3, 2, 3, 1, 2, 4, 5, 5, 6]
k = 4
solution = Solution()
print(solution.findKthLargest(nums, k))  # 输出 4
```

**解释**：数组中第四大的元素是 `4`。

---

### **总结**
- 对于这类题目，我们可以通过堆或快速选择来优化查找过程。
- 使用堆的时间复杂度是 `O(n log k)`，而使用快速选择法可以在平均 `O(n)` 的时间内完成查找。
- 根据题目要求和数据规模，我们可以选择最合适的方法来求解。
