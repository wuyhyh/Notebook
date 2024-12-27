以下是 **LRU 缓存 (Least Recently Used Cache)** 的总结文档，包括问题背景、解题思路、数据结构设计、代码实现、时间复杂度、空间复杂度等内容。

---

# LRU 缓存（Least Recently Used Cache）总结文档

## 1. 题目背景

LRU 缓存（Least Recently Used）是一种缓存淘汰策略，旨在保留最常使用的元素，而最久未使用的元素会被淘汰。LRU 缓存可以有效地提高缓存的命中率，常用于数据库、操作系统缓存管理等场景。

在 LeetCode 第 146 题中，要求我们设计一个 LRU 缓存的数据结构，支持以下两种操作：

- **`get(key)`**：如果缓存中存在 `key`，返回其值，否则返回 `-1`。
- **`put(key, value)`**：将 `key-value` 对存入缓存。如果缓存容量已满，则在插入新元素之前，移除最久未使用的元素。

缓存应当遵循 **LRU** 规则，即：最近使用的元素会被移到最前面，最久未使用的元素会被移除。

## 2. 解题思路

为了高效地支持两种操作，我们采用以下数据结构组合：

- **哈希表**：通过哈希表可以在 `O(1)` 时间内查找缓存中的元素。
- **双向链表**：双向链表可以在 `O(1)` 时间内进行节点的插入和删除操作。通过双向链表维护元素的访问顺序，链表头部表示最近使用的元素，链表尾部表示最久未使用的元素。

### 操作流程

- **`get(key)`**：查找缓存中的值。如果存在，更新该元素的访问顺序（将该元素移到链表头部）。如果不存在，返回 `-1`。
- **`put(key, value)`**：首先检查 `key` 是否已存在。如果存在，更新该元素的值，并将其移到链表头部；如果不存在，插入新的 `key-value` 对。如果缓存已满，删除链表尾部的元素，并从哈希表中删除对应的 `key`。

## 3. 数据结构设计

### 哈希表

使用哈希表 `cache` 来存储缓存中的数据，其中 `key` 为键，`value` 为链表节点。通过哈希表可以快速访问链表节点。

### 双向链表

双向链表用于维护缓存元素的访问顺序。链表的头部表示最近使用的元素，尾部表示最久未使用的元素。

### 哑节点

为了简化链表操作，我们使用两个哑节点 `head` 和 `tail`，分别表示链表的头和尾。`head.next` 指向链表的第一个有效节点，`tail.prev` 指向链表的最后一个有效节点。

## 4. 代码实现

### `DListNode` 类（双向链表节点）

```python
class DListNode:
    def __init__(self, key=0, value=0):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None
```

### `LRUCache` 类（LRU 缓存）

```python
class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = {}  # 哈希表存储键值对
        self.head = DListNode()  # 哑节点，链表头部
        self.tail = DListNode()  # 哑节点，链表尾部
        self.head.next = self.tail  # 初始时头尾连接
        self.tail.prev = self.head  # 初始时头尾连接

    def _remove(self, node: DListNode):
        """移除链表中的某个节点"""
        prev, next = node.prev, node.next
        prev.next, next.prev = next, prev

    def _add(self, node: DListNode):
        """将某个节点添加到链表头部"""
        next = self.head.next
        self.head.next = node
        node.prev = self.head
        node.next = next
        next.prev = node

    def get(self, key: int) -> int:
        """获取缓存中的值，如果不存在返回 -1"""
        if key in self.cache:
            node = self.cache[key]
            self._remove(node)
            self._add(node)  # 移到链表头部
            return node.value
        return -1

    def put(self, key: int, value: int) -> None:
        """插入或更新缓存"""
        if key in self.cache:
            node = self.cache[key]
            node.value = value  # 更新值
            self._remove(node)
            self._add(node)  # 移动到链表头部
        else:
            if len(self.cache) >= self.capacity:
                # 缓存已满，移除链表尾部的节点
                tail = self.tail.prev
                self._remove(tail)
                del self.cache[tail.key]
            # 插入新节点
            new_node = DListNode(key, value)
            self.cache[key] = new_node
            self._add(new_node)  # 添加到链表头部
```

## 5. 时间复杂度

- **`get(key)`**：`O(1)`。通过哈希表可以在常数时间内查找元素，同时将其移到链表头部的操作也是常数时间。
- **`put(key, value)`**：`O(1)`。通过哈希表可以在常数时间内查找、插入和更新元素，链表的插入和删除操作也是常数时间。如果缓存满了，移除尾部元素也是 `O(1)` 操作。

## 6. 空间复杂度

- **`O(capacity)`**：哈希表存储 `key-value` 对，链表存储所有的节点，空间复杂度与缓存容量成正比。

## 7. 示例解析

### 示例 1：

```python
lru = LRUCache(2)
lru.put(1, 1)
lru.put(2, 2)
print(lru.get(1))  # 返回 1
lru.put(3, 3)  # 该操作会把 key 2 移除
print(lru.get(2))  # 返回 -1 (未找到)
lru.put(4, 4)  # 该操作会把 key 1 移除
print(lru.get(1))  # 返回 -1 (未找到)
print(lru.get(3))  # 返回 3
print(lru.get(4))  # 返回 4
```

**输出**：

```plaintext
1
-1
-1
3
4
```

### 示例 2：

```python
lru = LRUCache(3)
lru.put(1, 1)
lru.put(2, 2)
lru.put(3, 3)
lru.put(4, 4)
print(lru.get(4))  # 返回 4
print(lru.get(3))  # 返回 3
print(lru.get(2))  # 返回 2
print(lru.get(1))  # 返回 -1 (未找到)
```

**输出**：

```plaintext
4
3
2
-1
```

## 8. 总结

| 操作   | 时间复杂度     | 空间复杂度     | 适用场景              |
|--------|----------------|----------------|-----------------------|
| `get`  | `O(1)`         | `O(capacity)`   | 支持快速查找缓存项     |
| `put`  | `O(1)`         | `O(capacity)`   | 支持快速插入和更新     |

LRU 缓存通过哈希表和双向链表的结合，实现了高效的缓存淘汰机制，能在 `O(1)` 时间内完成 `get` 和 `put` 操作，广泛应用于实际缓存系统中。
