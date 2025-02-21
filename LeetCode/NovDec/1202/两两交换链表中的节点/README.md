第24题是**“两两交换链表中的节点”**（Swap Nodes in Pairs），要求交换链表中每两个相邻的节点，并返回交换后的链表。

### 问题描述

给定一个链表，交换每两个相邻的节点，并返回交换后的链表。如果节点数为奇数，则最后一个节点保持不变。

### 示例

**示例 1:**

输入：
```plaintext
head = [1, 2, 3, 4]
```

输出：
```plaintext
[2, 1, 4, 3]
```

**示例 2:**

输入：
```plaintext
head = [1, 2, 3]
```

输出：
```plaintext
[2, 1, 3]
```

### 解题思路

这道题的核心在于如何交换相邻的两个节点。可以通过 **迭代法** 或 **递归法** 来解决，下面我们采用 **迭代法**，这种方法更直观且效率更高。

#### 迭代法步骤：

1. **创建虚拟头节点**：
    - 为了简化处理链表头节点的特殊情况（例如链表长度为 2 或 1），我们可以创建一个虚拟头节点 `dummy`，其 `next` 指向链表的头节点。

2. **初始化指针**：
    - 创建一个指针 `prev`，指向虚拟头节点 `dummy`，用来帮助交换节点。
    - 使用 `current` 指针来遍历链表。

3. **交换节点**：
    - 在每一步中，检查 `current` 是否能成对地进行交换（即检查 `current` 和 `current.next` 是否存在）。
    - 交换 `current` 和 `current.next` 的位置。
    - 更新 `prev` 和 `current` 的指针位置。

4. **处理链表的结尾**：
    - 如果链表长度是奇数，最后一个节点不会被交换，继续按正常的流程处理。

5. **返回结果**：
    - 返回虚拟头节点 `dummy.next`，即交换后的链表的头节点。

### 代码实现

```python
# Definition for singly-linked list.
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def swapPairs(head: ListNode) -> ListNode:
    # 创建一个虚拟头节点
    dummy = ListNode(0)
    dummy.next = head
    prev = dummy  # prev 用来指向要交换节点的前一个节点
    
    # 遍历链表
    while head and head.next:
        # 记录两个要交换的节点
        first = head
        second = head.next
        
        # 交换节点
        prev.next = second  # prev 指向第二个节点
        first.next = second.next  # 第一个节点指向第二个节点之后的节点
        second.next = first  # 第二个节点指向第一个节点
        
        # 移动 prev 和 head 指针
        prev = first
        head = first.next
    
    # 返回交换后的链表
    return dummy.next
```

### 代码解释

1. **虚拟头节点**：
    - 创建一个虚拟头节点 `dummy`，并将其 `next` 指向链表的头节点。这样可以方便处理头节点交换的特殊情况。

2. **prev 和 head 指针**：
    - `prev` 指向当前交换的前一个节点，初始化为虚拟头节点。
    - `head` 指向当前需要交换的第一个节点。

3. **交换逻辑**：
    - 如果当前节点 `head` 和 `head.next` 存在（即存在可以交换的节点对），则交换这两个节点。
    - 具体交换方式是：`prev.next` 指向 `head.next`（即第二个节点），`first.next` 指向 `second.next`（即第三个节点），`second.next` 指向 `first`（即第一个节点）。

4. **更新指针**：
    - `prev` 更新为 `first`，即交换后的第一个节点。
    - `head` 更新为 `first.next`，即交换后的第二个节点。

5. **返回结果**：
    - 返回 `dummy.next`，即最终交换后的链表头节点。

### 时间复杂度和空间复杂度

- **时间复杂度**：`O(n)`，其中 `n` 是链表的长度。我们需要遍历链表一次，每次处理两个节点。
- **空间复杂度**：`O(1)`，我们只用了常数空间来存储指针，链表本身没有额外的空间开销。

### 总结

1. **虚拟头节点**：通过创建虚拟头节点来简化链表的处理，避免特殊情况的处理。
2. **迭代法**：使用迭代法交换链表中的相邻节点，每次交换两个节点，并移动指针。
3. **时间复杂度**：`O(n)`，空间复杂度 `O(1)`。

这种方法简洁且高效，适用于链表节点交换的问题。如果你有任何问题或需要进一步的帮助，随时告诉我！