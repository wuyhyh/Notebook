第141题是“环形链表”（Linked List Cycle），要求判断一个链表是否有环。如果链表有环，返回 `True`，否则返回 `False`。

### 问题描述

给定一个链表，判断链表中是否存在环。

**环** 是指链表中的一个节点，指向其前面的一个节点，从而形成一个环状结构。

### 示例

**示例 1:**

输入：
```plaintext
head = [3, 2, 0, -4], pos = 1
```

输出：
```plaintext
True
```

解释：
链表中有环，其尾部连接到节点 1（索引从 0 开始）。

**示例 2:**

输入：
```plaintext
head = [1, 2], pos = 0
```

输出：
```plaintext
True
```

**示例 3:**

输入：
```plaintext
head = [1], pos = -1
```

输出：
```plaintext
False
```

### 解题思路

判断一个链表是否有环，最常见的方式是使用 **快慢指针**（又称为 **Floyd's Tortoise and Hare Algorithm**）。该方法通过两个指针分别以不同的速度遍历链表来检测是否有环。

### 思路分析

1. **快慢指针**：
    - 使用两个指针：一个慢指针 `slow` 每次走一步，一个快指针 `fast` 每次走两步。
    - 如果链表没有环，快指针最终会指向 `null`，表示链表结束。
    - 如果链表有环，快慢指针最终会相遇。

2. **为什么有效**：
    - 如果链表有环，快指针会比慢指针走得快，它们最终会相遇，因为快指针的速度是慢指针的两倍。
    - 如果链表没有环，快指针会在到达链表尾部时指向 `null`。

### 代码实现

```python
# Definition for singly-linked list.
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def hasCycle(head: ListNode) -> bool:
    if not head:
        return False
    
    slow, fast = head, head
    
    while fast and fast.next:
        slow = slow.next        # 慢指针走一步
        fast = fast.next.next   # 快指针走两步
        
        if slow == fast:        # 如果快慢指针相遇，说明有环
            return True
    
    return False  # 如果快指针指向 None，说明没有环
```

### 代码解释

1. **边界情况**：
    - 如果链表为空（`head == None`），直接返回 `False`，因为空链表没有环。

2. **初始化快慢指针**：
    - `slow` 和 `fast` 都初始化为链表的头节点。

3. **快慢指针遍历链表**：
    - 在 `while fast and fast.next` 循环中，快指针每次走两步，慢指针每次走一步。
    - 如果快指针和慢指针相遇（`slow == fast`），说明链表中有环，返回 `True`。
    - 如果快指针到达链表尾部（即 `fast == None` 或 `fast.next == None`），说明链表没有环，返回 `False`。

### 时间复杂度和空间复杂度

- **时间复杂度**：`O(n)`，其中 `n` 是链表的长度。由于快指针和慢指针都至少会遍历一次链表的节点，时间复杂度为线性。
- **空间复杂度**：`O(1)`，只使用了常数的空间来存储指针，空间复杂度是常数级别。

### 总结

1. **快慢指针法**：通过两个指针，慢指针走一步，快指针走两步，来检测链表中是否有环。
2. **时间复杂度**：`O(n)`，**空间复杂度**：`O(1)`，这是最优解。

这种方法非常高效且简单，能够在不使用额外空间的情况下完成环的检测。如果有任何问题，随时告诉我！
