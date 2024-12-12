### **LeetCode 第287题 - 寻找重复数 (Find the Duplicate Number)**

#### **题目描述**
给定一个包含 `n + 1` 个整数的数组，其中每个整数都在 `1` 到 `n` 之间，且至少有一个重复元素。要求在 **O(n)** 时间复杂度和 **O(1)** 空间复杂度内找到重复的元素。

---

### **解题思路**

本题可以通过 **二分查找** 和 **快慢指针法**（Floyd's Tortoise and Hare）来解决。考虑到题目要求 **O(n)** 的时间复杂度和 **O(1)** 的空间复杂度，因此我们不可以使用额外的数组或者哈希表。这里主要介绍 **快慢指针法**，它是一种经典的链表环检测方法，但由于数组的索引也是类似指针的作用，所以可以在数组中使用类似的方法来找到重复元素。

#### **快慢指针法**（Floyd's Tortoise and Hare）
1. **构建一个链表结构**：
    - 数组中的元素本身可以看作是一个链表的节点，值为 `nums[i]` 的元素指向位置 `nums[nums[i]]`。由于存在重复元素，数组实际上会形成一个环。

2. **步骤**：
    - **第一阶段**：使用快慢指针，慢指针每次移动一步，快指针每次移动两步。如果存在重复元素，快慢指针最终会在某个位置相遇（即指向同一个元素），这时说明数组中有环。
    - **第二阶段**：将其中一个指针移到数组的起点，两个指针同时以相同的速度（每次一步）移动，最终它们会相遇在环的起始位置，也就是重复的数字。

#### **算法步骤**：
1. 使用快慢指针初始化：`slow = nums[0]`，`fast = nums[0]`。
2. 在 `slow` 和 `fast` 指针相遇之前，`slow` 每次移动一步，`fast` 每次移动两步。
3. 当快慢指针相遇后，重新将 `slow` 指针移到数组的起点，然后让两个指针同时以步长为1的速度向前移动，最终它们会相遇在重复的元素上。

---

### **代码实现**

```python
class Solution:
    def findDuplicate(self, nums):
        # Phase 1: Find the intersection point of the two runners
        slow = nums[0]
        fast = nums[0]
        
        # Step 1: Move slow by 1 step, fast by 2 steps until they meet
        while True:
            slow = nums[slow]
            fast = nums[nums[fast]]
            if slow == fast:
                break
        
        # Phase 2: Find the entry point to the cycle
        slow = nums[0]
        while slow != fast:
            slow = nums[slow]
            fast = nums[fast]
        
        return slow
```

### **代码解析**

1. **第一阶段：寻找相遇点**  
   在这阶段，使用慢指针 `slow` 每次移动一步，快指针 `fast` 每次移动两步。由于存在重复元素，它们最终会在某个地方相遇。相遇的地方可以看作是环内的一个点。

2. **第二阶段：寻找环的入口**  
   当快慢指针相遇时，将 `slow` 指针重新指向数组的起点，接着同时让 `slow` 和 `fast` 指针每次移动一步，直到它们再次相遇，那个相遇的点即为重复的数字。

3. **返回值**：返回重复的数字，即相遇点。

### **时间复杂度**
- **时间复杂度**：`O(n)`。第一次循环是通过快慢指针找到环的相遇点，第二次循环是找到环的入口，总体时间复杂度为 `O(n)`。

### **空间复杂度**
- **空间复杂度**：`O(1)`。我们仅使用了常数空间，快慢指针和输入数组不需要额外的空间。

---

### **示例测试**

#### 示例 1：
```python
nums = [1, 3, 4, 2, 2]
solution = Solution()
print(solution.findDuplicate(nums))  # 输出 2
```

#### 示例 2：
```python
nums = [3, 1, 3, 4, 2]
solution = Solution()
print(solution.findDuplicate(nums))  # 输出 3
```

---

### **总结**
- 本题的关键是利用 **快慢指针法** 来寻找重复元素。通过将数组视作一个链表，利用链表环的特点来找到重复元素的位置。
- 时间复杂度为 `O(n)`，空间复杂度为 `O(1)`，符合题目要求的时间和空间限制。
