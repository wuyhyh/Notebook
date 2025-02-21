LeetCode 第148题是 **排序链表**，该题要求我们对一个链表进行排序，返回排序后的链表。

### 题目描述

给定一个链表的头节点 `head`，请返回链表排序后的头节点。

#### 示例

**示例 1:**

```plaintext
输入: 4->2->1->3
输出: 1->2->3->4
```

**示例 2:**

```plaintext
输入: -1->5->3->4->0
输出: -1->0->3->4->5
```

#### 解题思路

这个问题要求我们对一个链表进行排序。直接的排序方法（如冒泡排序、插入排序等）效率较低，因此我们需要一种更高效的方法来解决这个问题。

1. **归并排序（Merge Sort）**：
    - 归并排序是一种稳定排序算法，时间复杂度为 `O(n log n)`，非常适合用于链表排序。
    - 对链表进行归并排序的步骤是：
        1. **分割链表**：我们将链表从中间分成两部分。
        2. **递归排序**：对两部分链表递归排序。
        3. **合并两个有序链表**：将两个已排序的链表合并成一个有序链表。

   由于链表的性质，我们不需要像数组那样使用额外的空间来进行分割，而是通过指针操作实现链表的分割和合并。

#### 代码实现

```python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

class Solution:
    def sortList(self, head: ListNode) -> ListNode:
        if not head or not head.next:
            return head
        
        # 使用快慢指针找到中点
        slow, fast = head, head
        prev = None
        while fast and fast.next:
            prev = slow
            slow = slow.next
            fast = fast.next.next
        
        # 切断链表
        prev.next = None
        
        # 递归地排序两个部分
        left = self.sortList(head)
        right = self.sortList(slow)
        
        # 合并两个已排序的链表
        return self.merge(left, right)
    
    def merge(self, left: ListNode, right: ListNode) -> ListNode:
        dummy = ListNode()
        current = dummy
        
        while left and right:
            if left.val < right.val:
                current.next = left
                left = left.next
            else:
                current.next = right
                right = right.next
            current = current.next
        
        # 将剩余的节点接到结果链表后
        if left:
            current.next = left
        if right:
            current.next = right
        
        return dummy.next
```

### 代码解释

1. **`sortList` 方法**：
    - 如果链表为空或只有一个元素，则返回该链表（即已经排序）。
    - 使用 **快慢指针** 找到链表的中间节点：
        - `slow` 指针每次走一步，`fast` 指针每次走两步，当 `fast` 指针到达链表末尾时，`slow` 指针正好处于链表的中间。
    - 将链表从中间分开，递归地对左右两部分进行排序。
    - 最后将两个已排序的链表合并。

2. **`merge` 方法**：
    - 合并两个已排序的链表。
    - 使用一个虚拟头节点（`dummy`）来简化合并过程。
    - 比较两个链表的头节点，选择较小的节点将其连接到结果链表中。
    - 如果有剩余的节点，直接将其连接到结果链表的末尾。

### 时间复杂度

- **时间复杂度**：`O(n log n)`，其中 `n` 是链表的节点数。归并排序的时间复杂度是 `O(n log n)`，每次分割链表时进行合并操作。
- **空间复杂度**：`O(log n)`，递归的栈空间，归并排序的递归深度是 `O(log n)`。

### 示例

#### 示例 1

输入：

```plaintext
4 -> 2 -> 1 -> 3
```

执行排序后，输出：

```plaintext
1 -> 2 -> 3 -> 4
```

#### 示例 2

输入：

```plaintext
-1 -> 5 -> 3 -> 4 -> 0
```

执行排序后，输出：

```plaintext
-1 -> 0 -> 3 -> 4 -> 5
```

### 总结

| 操作       | 时间复杂度    | 空间复杂度   |
|------------|---------------|--------------|
| `sortList` | `O(n log n)`  | `O(log n)`   |
| `merge`    | `O(n)`        | `O(1)`       |

- 归并排序是解决链表排序问题的理想选择，因为它能在 `O(n log n)` 时间复杂度内完成排序，而且不需要额外的空间来存储链表元素，适合链表这种线性结构。
