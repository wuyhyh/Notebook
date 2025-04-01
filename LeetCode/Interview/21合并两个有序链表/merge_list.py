from typing import Optional


class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

    def print_list(self):
        result = []
        current = self
        while current:
            result.append(str(current.val))
            current = current.next
        return "->".join(result)


class Solution:
    def merge_two_lists(self, l1: ListNode, l2: ListNode) -> ListNode:
        # 创建虚拟头结点
        dummy = ListNode(-1)
        current = dummy

        # 遍历两个节点，选择较小的节点连接
        while l1 and l2:
            if l1.val < l2.val:
                current.next = l1
                l1 = l1.next
            else:
                current.next = l2
                l2 = l2.next
            current = current.next  # current也要前进

        # 剩余的节点直接连接
        current.next = l1 if l1 else l2

        return dummy.next


if __name__ == '__main__':
    l1 = ListNode(1, ListNode(2, ListNode(4)))
    l2 = ListNode(1, ListNode(3, ListNode(4)))
    solution = Solution()
    merged = solution.merge_two_lists(l1, l2)
    print(merged.print_list())
