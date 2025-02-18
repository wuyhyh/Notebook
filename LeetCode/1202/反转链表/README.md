第206题是“反转链表”（Reverse Linked List），要求反转一个单链表。

### 问题描述

给定一个单链表的头节点 `head`，将链表反转并返回其新的头节点。

### 示例

**示例 1:**

输入：
```plaintext
head = [1, 2, 3, 4, 5]
```

输出：
```plaintext
[5, 4, 3, 2, 1]
```

**示例 2:**

输入：
```plaintext
head = [1, 2]
```

输出：
```plaintext
[2, 1]
```

**示例 3:**

输入：
```plaintext
head = []
```

输出：
```plaintext
[]
```

### 解题思路

反转单链表的思路是通过 **迭代** 或 **递归** 逐步改变链表中每个节点的指向，使得每个节点的 `next` 指针指向它的前一个节点。最终，我们将返回新的链表头节点（即原来链表的最后一个节点）。

### 迭代方法

1. **初始化三个指针**：
    - `prev`：指向当前节点的前一个节点，初始化为 `None`。
    - `curr`：指向当前节点，初始化为链表的头节点 `head`。
    - `next_node`：临时存储 `curr.next`，防止丢失下一个节点。

2. **迭代过程**：
    - 遍历链表，对于每个节点，将它的 `next` 指针指向 `prev`。
    - 然后将 `prev` 移动到当前节点，将 `curr` 移动到下一个节点，继续这个过程。

3. **结束时**，`curr` 将变成 `None`，`prev` 会指向新的头节点（即反转后的链表头节点）。

### 代码实现

```python
# Definition for singly-linked list.
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def reverseList(head: ListNode) -> ListNode:
    prev = None
    curr = head
    
    while curr:
        next_node = curr.next   # 暂存当前节点的下一个节点
        curr.next = prev       # 反转当前节点的指向
        prev = curr            # prev 移动到当前节点
        curr = next_node       # curr 移动到下一个节点
    
    return prev  # prev 最终指向新链表的头节点
```

### 代码解释

1. **初始化**：
    - `prev`：初始化为 `None`，因为反转后的链表头节点的 `next` 必须指向 `None`。
    - `curr`：初始化为链表的头节点 `head`，用于遍历链表。

2. **循环遍历链表**：
    - `next_node = curr.next`：暂时保存当前节点的下一个节点，防止指针丢失。
    - `curr.next = prev`：反转当前节点的指向，使其指向 `prev`。
    - `prev = curr`：将 `prev` 移动到当前节点。
    - `curr = next_node`：将 `curr` 移动到下一个节点。

3. **返回结果**：
    - `prev` 指向反转后的链表的头节点，因此返回 `prev`。

### 时间复杂度和空间复杂度

- **时间复杂度**：`O(n)`，其中 `n` 是链表的长度。我们需要遍历链表中的每个节点一次。
- **空间复杂度**：`O(1)`，我们只用了常数空间来存储指针。

### 总结

1. **迭代方法**：通过三个指针 `prev`、`curr` 和 `next_node` 逐步反转链表中的每个节点。
2. **时间复杂度** 为 `O(n)`，**空间复杂度** 为 `O(1)`，这是最优解。

如果你有任何问题或需要进一步的解释，随时告诉我！