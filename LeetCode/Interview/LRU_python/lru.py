class Node:
    def __init__(self, key=0, value=0):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None


class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = {}
        # 伪首部和尾部
        self.head = Node()
        self.tail = Node()
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node: Node):
        """从链表中移除节点"""
        prev, next = node.prev, node.next
        prev.next = next
        next.prev = prev

    def _add_to_end(self, node: Node):
        """将节点添加到链表尾部"""
        prev, next = self.tail.prev, self.tail
        prev.next = node
        node.prev = prev
        node.next = next
        next.prev = node

    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        node = self.cache[key]
        self._remove(node)
        self._add_to_end(node)
        return node.value

    def put(self, key: int, value: int) -> Node:
        if key in self.cache:
            """更新值，并移动到队尾"""
            node = self.cache[key]
            node.value = value
            self._remove(node)
            self._add_to_end(node)
        else:
            """新增节点，移除最久未使用节点"""
            if len(self.cache) >= self.capacity:
                lru = self.head.next
                self._remove(lru)
                del self.cache[lru.key]
            node = Node(key, value)
            self.cache[key] = node
            self._add_to_end(node)
