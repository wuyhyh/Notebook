第138题是 **“复制带随机指针的链表”**（Copy List with Random Pointer）。该题要求我们复制一个链表，其中每个节点不仅有一个 `next` 指针指向下一个节点，还有一个 `random` 指针指向链表中的任意节点（或可能是 `null`）。

### 问题描述

每个节点都包含：
- `val`：节点的值。
- `next`：指向下一个节点的指针。
- `random`：指向链表中的任意节点或 `null` 的指针。

请你返回 **新复制的链表**，其结构与原链表相同，但其中的 `random` 指针指向的节点也需要被复制。

### 示例

**示例 1:**

输入：
```plaintext
head = [[7,null],[13,0],[11,4],[10,2],[1,0]]
```

输出：
```plaintext
[[7,null],[13,0],[11,4],[10,2],[1,0]]
```

**示例 2:**

输入：
```plaintext
head = [[1,1],[2,1]]
```

输出：
```plaintext
[[1,1],[2,1]]
```

**示例 3:**

输入：
```plaintext
head = [[3,null],[3,0],[3,null]]
```

输出：
```plaintext
[[3,null],[3,0],[3,null]]
```

### 解题思路

这道题的关键点在于如何同时复制链表的 `next` 和 `random` 指针。我们可以通过以下步骤来解决：

#### 步骤：

1. **创建新节点并插入原链表中**：
    - 我们遍历原链表，在每个节点后面插入一个新的节点，新的节点的 `next` 指针指向原链表的下一个节点。
    - 这样，新节点和原节点的顺序就交替排列，例如：`1 -> 1' -> 2 -> 2' -> 3 -> 3' -> ...`。

2. **设置新节点的 `random` 指针**：
    - 由于新节点是紧跟着原节点的，所以新节点的 `random` 指针可以通过原节点的 `random` 指针来直接访问。
    - 如果原节点的 `random` 指针指向节点 `A`，那么新节点的 `random` 应该指向节点 `A.next`（即 `A` 的复制节点）。

3. **分离链表**：
    - 新节点已经和原节点交替连接起来，现在我们需要将它们拆分成两条链表。原链表恢复原状，而新链表指向复制后的节点。

### 代码实现

```python
# Definition for a Node.
class Node:
    def __init__(self, val=0, next=None, random=None):
        self.val = val
        self.next = next
        self.random = random

def copyRandomList(head: Node) -> Node:
    if not head:
        return None

    # 第一步：复制节点并将新节点插入到原节点后面
    current = head
    while current:
        new_node = Node(current.val)
        new_node.next = current.next
        current.next = new_node
        current = new_node.next

    # 第二步：设置每个新节点的 random 指针
    current = head
    while current:
        if current.random:
            current.next.random = current.random.next
        current = current.next.next

    # 第三步：拆分链表，恢复原链表并提取新链表
    original = head
    copy = head.next
    new_head = head.next
    while original:
        original.next = original.next.next
        if copy.next:
            copy.next = copy.next.next
            copy = copy.next
        original = original.next

    return new_head
```

### 代码解释

1. **复制节点并插入原链表中**：
    - 我们遍历链表，对于每个节点 `current`，创建一个新节点 `new_node`，然后将 `new_node` 插入到 `current` 和 `current.next` 之间。
    - 这样做的目的是让新节点和原节点交替排列。例如，如果原链表是 `A -> B -> C`，则复制后链表为 `A -> A' -> B -> B' -> C -> C'`。

2. **设置 `random` 指针**：
    - 通过遍历链表，对于每个节点 `current`，如果其 `random` 指针不为空，我们将 `current.next.random` 设置为 `current.random.next`，即让新节点的 `random` 指向原节点 `random` 指向的节点的复制。

3. **分离链表**：
    - 我们通过两个指针 `original` 和 `copy` 来分别指向原链表和新链表的头部。
    - 遍历链表时，我们通过调整 `original.next` 和 `copy.next` 来分离出两个链表：原链表和复制链表。

4. **返回新链表头**：
    - 最终返回新链表的头节点 `new_head`，这是 `head.next`，因为新链表是从 `head.next` 开始的。

### 时间复杂度和空间复杂度

- **时间复杂度**：`O(n)`，其中 `n` 是链表的长度。我们遍历链表三次：第一次插入新节点，第二次设置 `random` 指针，第三次分离链表。
- **空间复杂度**：`O(n)`，因为我们需要为每个原节点创建一个新节点。

### 总结

1. **插入新节点**：通过在原链表中插入新节点，解决了如何同时复制 `next` 和 `random` 指针的问题。
2. **设置 `random` 指针**：通过利用原链表节点的 `random` 指针来设置新节点的 `random` 指针。
3. **链表拆分**：通过分离链表来恢复原链表，并提取出新链表。

这种方法既高效又简单，非常适合处理带有 `random` 指针的链表问题。如果你有任何问题，随时告诉我！