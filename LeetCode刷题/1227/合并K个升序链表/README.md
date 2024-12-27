### 题目：LeetCode 第23题 **合并 K 个升序链表**

#### 题目描述

给定一个链表数组，每个链表都按升序排列，请将所有链表合并为一个升序链表。返回合并后的链表。

#### 示例

**示例 1:**

```plaintext
输入:
[1->4->5, 1->3->4, 2->6]
输出:
1->1->2->3->4->4->5->6
```

**示例 2:**

```plaintext
输入:
[]
输出:
[]
```

**示例 3:**

```plaintext
输入:
[[]]
输出:
[]
```

#### 解题思路

1. **使用优先队列（最小堆）**：
    - 我们可以利用 Python 的 `heapq` 模块实现一个最小堆（优先队列），每次从堆中取出最小节点，插入合并链表。
    - 每个链表的头节点被放入堆中，堆会自动保持升序。
    - 每次从堆中弹出最小节点，如果该节点所在的链表还有剩余节点，则将下一个节点插入堆中，直到所有节点都被处理完。

2. **不能直接比较 `ListNode`**：
    - 在在线判题系统中，`ListNode` 可能没有比较方法（如 `__lt__`），因此无法直接使用 `heapq` 进行比较。
    - 解决方案：使用包装类 `Wrapper` 来封装 `ListNode`，并通过 `Wrapper` 类的 `__lt__` 方法进行节点的比较，确保堆按升序排列。

#### 代码实现

```python
import heapq

# 封装 ListNode 的包装类
class Wrapper:
    def __init__(self, node):
        self.node = node
    
    def __lt__(self, other):
        # 比较节点的值，用于堆的排序
        return self.node.val < other.node.val
    
    def __repr__(self):
        return f"Wrapper({self.node.val})"

class Solution:
    def mergeKLists(self, lists):
        # 初始化一个最小堆
        heap = []
        
        # 将所有链表的头节点放入堆中
        for l in lists:
            if l:
                # 将 ListNode 封装成 Wrapper 对象并插入堆
                heapq.heappush(heap, Wrapper(l))
        
        # 创建一个虚拟头节点，方便构造合并后的链表
        dummy = ListNode()
        current = dummy
        
        # 从堆中取出最小元素，并将其下一个节点放入堆中
        while heap:
            # 取出堆顶元素（即值最小的节点）
            wrapper = heapq.heappop(heap)
            node = wrapper.node
            current.next = node
            current = current.next
            
            # 如果该链表有下一个节点，插入堆中
            if node.next:
                heapq.heappush(heap, Wrapper(node.next))
        
        # 返回合并后的链表头
        return dummy.next
```

#### 代码解释

1. **`Wrapper` 类**：
    - `Wrapper` 类封装了 `ListNode` 节点，并实现了 `__lt__` 方法，使得 `heapq` 能够根据节点值进行排序。
    - `__lt__` 方法返回 `True`，如果当前节点的值小于另一个节点的值，从而确保堆中始终保持最小堆。

2. **`mergeKLists` 方法**：
    - 将每个链表的头节点封装为 `Wrapper` 对象，并插入到最小堆中。
    - 从堆中弹出最小元素，将其连接到合并链表中。如果该节点所在链表有剩余节点，则将其下一个节点继续插入堆中。
    - 最终返回合并后的链表。

#### 时间复杂度

- 插入堆和弹出堆的时间复杂度为 `O(log K)`，其中 `K` 是链表的数量。
- 每个链表节点都会被插入和弹出堆一次，总的时间复杂度是 `O(N log K)`，其中 `N` 是所有链表的节点总数。

#### 空间复杂度

- 堆中最多存储 `K` 个元素，因此空间复杂度为 `O(K)`，其中 `K` 是链表的数量。

#### 结论

通过使用 `Wrapper` 类来包装 `ListNode`，并在 `__lt__` 方法中实现节点值的比较，我们能够在不修改 `ListNode` 类的前提下顺利地使用 `heapq` 实现合并 K 个升序链表的功能。这种方法简单且高效，适用于需要合并多个链表的场景。
