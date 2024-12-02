第142题是“环形链表 II”（Linked List Cycle II），要求找出链表中环的入口节点。如果链表没有环，返回 `None`。

### 问题描述

给定一个链表，判断链表是否有环，并返回环的入口节点。如果没有环，返回 `None`。

### 示例

**示例 1:**

输入：
```plaintext
head = [3, 2, 0, -4], pos = 1
```

输出：
```plaintext
Node with value 2
```

解释：链表中有环，其尾部连接到节点 1（索引从 0 开始）。

**示例 2:**

输入：
```plaintext
head = [1, 2], pos = 0
```

输出：
```plaintext
Node with value 1
```

**示例 3:**

输入：
```plaintext
head = [1], pos = -1
```

输出：
```plaintext
None
```

### 解题思路

我们可以利用 **快慢指针法**（Floyd's Tortoise and Hare Algorithm）来解决这个问题。首先使用快慢指针检测链表中是否有环；然后，一旦快慢指针相遇，我们就能通过一个新的指针找到环的入口。

### 解题步骤

1. **检测链表是否有环**：
    - 使用两个指针：`slow`（慢指针）和 `fast`（快指针）。`slow` 每次走一步，`fast` 每次走两步。
    - 如果链表有环，快慢指针最终会相遇。

2. **找到环的入口**：
    - 一旦快慢指针相遇（说明链表有环），我们将其中一个指针移回链表头节点。
    - 然后让两个指针（一个从头节点开始，另一个从相遇点开始）同时每次走一步。
    - 它们最终会在环的入口相遇。

### 代码实现

```python
# Definition for singly-linked list.
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def detectCycle(head: ListNode) -> ListNode:
    if not head or not head.next:
        return None
    
    slow, fast = head, head
    
    # 步骤 1: 快慢指针相遇检测环
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        
        if slow == fast:  # 快慢指针相遇，说明有环
            # 步骤 2: 寻找环的入口
            pointer1 = head
            pointer2 = slow
            
            while pointer1 != pointer2:  # 让两指针一起走，直到它们相遇
                pointer1 = pointer1.next
                pointer2 = pointer2.next
            
            return pointer1  # 返回环的入口节点
    
    return None  # 没有环
```

### 代码解释

1. **快慢指针法检测环**：
    - `slow` 和 `fast` 指针同时从链表头开始，`slow` 每次走一步，`fast` 每次走两步。
    - 如果链表有环，快慢指针最终会在环内相遇。相遇时，我们可以确定链表中存在环。

2. **寻找环的入口**：
    - 一旦检测到环，指针 `pointer1` 重新指向链表头，`pointer2` 继续保持在慢指针相遇的位置。
    - 然后，两个指针 `pointer1` 和 `pointer2` 同时每次走一步，直到它们相遇。
    - 它们相遇的节点即为环的入口节点。

3. **没有环的情况**：
    - 如果链表没有环，`fast` 会在走到 `None` 时停止循环，直接返回 `None`。

### 时间复杂度和空间复杂度

- **时间复杂度**：`O(n)`，其中 `n` 是链表的长度。我们最多遍历两次链表：一次用于检测环，另一次用于找到环的入口。
- **空间复杂度**：`O(1)`，只使用了常数空间来存储指针。

### 总结

1. **快慢指针法**：通过快慢指针来检测链表是否有环。
2. **找到环的入口**：通过让其中一个指针返回链表头，另一个指针保持在相遇点，最终找到环的入口。
3. **时间复杂度**：`O(n)`，**空间复杂度**：`O(1)`，这是最优解。

这个解法利用了快慢指针来高效地解决了找环入口的问题。如果你有任何疑问，或者需要进一步的帮助，随时告诉我！