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
