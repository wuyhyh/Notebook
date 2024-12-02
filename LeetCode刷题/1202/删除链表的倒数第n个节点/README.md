好的，以下是整理好的文档，包含了解题思路、代码实现以及相关的解释。

---

# LeetCode 第19题：删除链表的倒数第 N 个节点

## 问题描述

给定一个链表，删除链表的倒数第 `n` 个节点，并返回链表的头节点。

### 示例

**示例 1:**

输入：
```plaintext
head = [1, 2, 3, 4, 5], n = 2
```

输出：
```plaintext
[1, 2, 3, 5]
```

**示例 2:**

输入：
```plaintext
head = [1], n = 1
```

输出：
```plaintext
[]
```

**示例 3:**

输入：
```plaintext
head = [1, 2], n = 1
```

输出：
```plaintext
[1]
```

## 解题思路

要删除链表的倒数第 `n` 个节点，我们可以使用 **双指针法**，这个方法通过维护两个指针之间的距离，来找到倒数第 `n` 个节点的前一个节点，从而完成删除操作。

### 具体步骤：

1. **初始化指针**：
    - 创建一个虚拟头节点 `dummy`，使得删除头节点的情况也能统一处理。
    - 设置两个指针 `fast` 和 `slow`，两个指针都从虚拟头节点开始。

2. **让第一个指针 `fast` 先走 `n` 步**：
    - 让 `fast` 指针先走 `n` 步，这样 `fast` 和 `slow` 之间的距离始终保持 `n`。

3. **同时移动两个指针 `fast` 和 `slow`**：
    - 让 `fast` 和 `slow` 同时每次走一步，直到 `fast` 指针到达链表的末尾。
    - 此时，`slow` 指针指向的是倒数第 `n` 个节点的前一个节点。

4. **删除节点**：
    - 通过调整 `slow.next` 指向 `slow.next.next` 来删除倒数第 `n` 个节点。

5. **返回结果**：
    - 返回虚拟头节点 `dummy` 的下一个节点，即新的链表头节点。

## 代码实现

```python
# Definition for singly-linked list.
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def removeNthFromEnd(head: ListNode, n: int) -> ListNode:
    # 创建一个虚拟头节点，方便删除头节点的情况
    dummy = ListNode(0)
    dummy.next = head
    fast = slow = dummy
    
    # 让fast指针先走n步
    for _ in range(n):
        fast = fast.next
    
    # 然后fast和slow一起走，直到fast到达链表末尾
    while fast.next:
        fast = fast.next
        slow = slow.next
    
    # 删除倒数第n个节点
    slow.next = slow.next.next
    
    return dummy.next
```

## 代码解释

1. **虚拟头节点**：
    - 使用一个虚拟节点 `dummy`，并将其 `next` 指向链表的头节点。这样处理可以统一删除头节点的情况。
    - 初始化 `fast` 和 `slow` 两个指针，它们都指向虚拟头节点。

2. **让 `fast` 指针先走 `n` 步**：
    - 使用 `for _ in range(n)` 循环，让 `fast` 指针先走 `n` 步。这样，`fast` 和 `slow` 之间的距离始终保持 `n`。

3. **同时移动 `fast` 和 `slow` 指针**：
    - 当 `fast` 指针到达链表末尾时，`slow` 指针正好停在倒数第 `n` 个节点的前一个节点。

4. **删除节点**：
    - 使用 `slow.next = slow.next.next` 来删除倒数第 `n` 个节点，直接将 `slow.next` 指向下一个节点。

5. **返回结果**：
    - 返回 `dummy.next`，即删除节点后的链表头节点。

## 时间复杂度和空间复杂度

- **时间复杂度**：`O(L)`，其中 `L` 是链表的长度。我们只需要遍历链表一次，找到倒数第 `n` 个节点并删除它。
- **空间复杂度**：`O(1)`，只用了常数空间存储指针。

## 总结

1. **双指针法**：通过快慢指针来找到倒数第 `n` 个节点的前一个节点。
2. **虚拟头节点**：通过创建虚拟头节点简化删除头节点的处理。
3. **时间复杂度**：`O(L)`，空间复杂度 `O(1)`，这是最优解。

这种方法高效且简洁，适用于链表操作中的删除节点问题。如果有任何问题，随时告诉我！