class DListNode:
    def __init__(self, key=0, value=0):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None


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
