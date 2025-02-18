好的，以下是整理好的文档，包含了解题思路、代码实现以及相关的解释。

---

# LeetCode 第25题：K 个一组翻转链表

## 问题描述

给定一个链表，每 `k` 个节点一组进行翻转。如果节点数不是 `k` 的倍数，则最后一组节点保持原样。

### 示例

**示例 1:**

输入：
```plaintext
head = [1, 2, 3, 4, 5], k = 3
```

输出：
```plaintext
[3, 2, 1, 4, 5]
```

**示例 2:**

输入：
```plaintext
head = [1, 2, 3, 4, 5], k = 2
```

输出：
```plaintext
[2, 1, 4, 3, 5]
```

**示例 3:**

输入：
```plaintext
head = [1, 2, 3, 4, 5], k = 6
```

输出：
```plaintext
[1, 2, 3, 4, 5]
```

## 解题思路

为了将链表中的每 `k` 个节点翻转，我们可以分成几个步骤来实现：

1. **检查是否有足够的节点进行翻转**：
    - 每次翻转之前，需要判断当前剩余的节点是否至少有 `k` 个。如果剩余节点数不足 `k`，则不进行翻转，直接返回链表。

2. **翻转每 `k` 个节点**：
    - 使用三个指针来进行节点翻转：`prev`、`cur` 和 `next`。
        - `prev`：指向翻转部分的前一个节点，帮助连接翻转后的部分。
        - `cur`：当前正在翻转的节点。
        - `next`：记录当前节点的下一个节点，用来控制翻转过程中的链表连接。

3. **连接翻转后的部分**：
    - 翻转完当前组的节点后，将翻转后的部分连接到剩余部分。

4. **递归或迭代**：
    - 对链表剩余的节点进行翻转，直到处理完所有节点。

### 代码实现

```python
# Definition for singly-linked list.
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def reverseKGroup(head: ListNode, k: int) -> ListNode:
    # 检查链表长度是否至少为 k
    def has_k_nodes(node, k):
        count = 0
        while node and count < k:
            node = node.next
            count += 1
        return count == k
    
    # 翻转链表的一部分
    def reverse_linked_list(start, k):
        prev = None
        cur = start
        while k > 0:
            next_node = cur.next
            cur.next = prev
            prev = cur
            cur = next_node
            k -= 1
        return prev, start  # 返回新的头节点和尾节点
    
    # 处理链表
    dummy = ListNode(0)
    dummy.next = head
    group_prev = dummy  # group_prev 用来连接翻转后的部分
    
    while head:
        if has_k_nodes(head, k):
            # 如果剩余的节点大于等于 k，则翻转这 k 个节点
            group_start = head
            group_end = head
            for _ in range(k - 1):
                group_end = group_end.next
            
            # 保存下一个部分
            next_group = group_end.next
            # 翻转当前 k 个节点
            new_head, new_tail = reverse_linked_list(group_start, k)
            
            # 连接翻转后的部分
            group_prev.next = new_head
            group_start.next = next_group
            group_prev = group_start
            head = next_group
        else:
            # 如果剩余节点不足 k，直接返回
            break
    
    return dummy.next
```

## 代码解释

1. **`has_k_nodes` 函数**：
    - 该函数用于判断链表中是否有足够的节点进行一次完整的翻转。如果剩余的节点数小于 `k`，则返回 `False`；否则返回 `True`。

2. **`reverse_linked_list` 函数**：
    - 该函数负责翻转链表中的一部分节点（`k` 个节点）。通过调整 `cur` 和 `prev` 两个指针的连接方式，完成这部分节点的翻转。

3. **主函数 `reverseKGroup`**：
    - 使用虚拟头节点 `dummy` 来简化操作，特别是处理头节点的翻转。
    - 使用 `group_prev` 指针来连接翻转后的部分。
    - 在每次处理一个完整的 `k` 个节点时，调用 `reverse_linked_list` 进行翻转，并且更新 `group_prev` 和 `head` 指针，继续处理剩余的部分。

4. **链表翻转后的连接**：
    - 通过 `group_prev.next = new_head` 来连接翻转后的头节点。
    - 通过 `group_start.next = next_group` 来连接翻转后的尾节点到剩余部分。

## 时间复杂度和空间复杂度

- **时间复杂度**：`O(n)`，其中 `n` 是链表的长度。我们只遍历一次链表，每次翻转的操作也是常数时间。
- **空间复杂度**：`O(1)`，我们只用了常数空间来进行翻转操作，不需要额外的空间。

## 总结

1. **链表分组**：每次处理链表中的 `k` 个节点，进行翻转操作。
2. **节点翻转**：通过三个指针 `prev`、`cur` 和 `next` 来翻转链表中的节点。
3. **时间复杂度**：`O(n)`，空间复杂度 `O(1)`，是最优解。

这种方法高效且简洁，适用于链表中的分组翻转问题。如果有任何问题，随时告诉我！