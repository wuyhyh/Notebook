### **LeetCode 第169题 - 多数元素**

#### **题目描述**
给定一个大小为 `n` 的数组 `nums`，找到其中的多数元素。多数元素是指在数组中出现次数大于 `n/2` 的元素。

你可以假设数组是非空的，并且给定的数组总是存在多数元素。

---

### **解题思路**

本题要求我们在 **O(n)** 时间复杂度和 **O(1)** 空间复杂度下找到多数元素。我们可以使用 **Boyer-Moore 投票算法** 来解决该问题。

#### **Boyer-Moore 投票算法**
这个算法的核心思想是：在遍历数组时通过不断地“投票”选举出一个候选多数元素，并最终确定该元素是否是多数元素。

##### **算法过程**：
1. **候选人选举**：
    - 我们维护一个候选元素 `candidate` 和一个计数器 `count`。初始时，`candidate` 为数组中的任意元素，`count` 为 0。
    - 遍历数组，每遇到一个元素：
        - 如果 `count` 为 0，更新 `candidate` 为当前元素，并将 `count` 设置为 1。
        - 如果当前元素和 `candidate` 相同，`count` 增加 1。
        - 如果当前元素和 `candidate` 不同，`count` 减少 1。

2. **最终结果**：
    - 遍历结束后，`candidate` 就是我们要找的多数元素。

**为什么这个算法有效**：
- 如果一个元素出现次数超过了数组的总大小的一半，那么它在投票过程中将最终成为候选元素。因为每当 `count` 为 0 时，我们会更新 `candidate`，并且多数元素会在相互抵消中“获胜”。

---

### **代码实现**

```python
class Solution:
    def majorityElement(self, nums):
        candidate = None
        count = 0
        
        # 第一遍遍历，选举出候选元素
        for num in nums:
            if count == 0:
                candidate = num
                count = 1
            elif num == candidate:
                count += 1
            else:
                count -= 1
        
        return candidate
```

---

### **代码解析**
1. **候选元素选举**：
    - 使用 `candidate` 变量记录当前的候选多数元素，`count` 记录其出现次数。
    - 遍历数组，如果当前元素和 `candidate` 相同，`count` 加 1；如果不同，`count` 减 1。
    - 当 `count` 为 0 时，更新候选元素为当前元素。

2. **最终结果**：
    - 遍历结束后，`candidate` 即为多数元素，符合题目保证条件。

---

### **复杂度分析**
- **时间复杂度**：`O(n)`，其中 `n` 是数组的长度。我们只遍历一次数组。
- **空间复杂度**：`O(1)`，我们只使用了常数级别的额外空间。

---

### **示例测试**

#### 示例 1：
```python
nums = [3, 2, 3]
solution = Solution()
print(solution.majorityElement(nums))  # 输出 3
```

#### 示例 2：
```python
nums = [2, 2, 1, 1, 1, 2, 2]
solution = Solution()
print(solution.majorityElement(nums))  # 输出 2
```

---

### **总结**
- **Boyer-Moore 投票算法**是一种高效的算法，能够在 **O(n)** 时间复杂度和 **O(1)** 空间复杂度下解决多数元素问题。
- 本题保证了多数元素的存在，因此只需要通过一次遍历就能找到最终的多数元素。
