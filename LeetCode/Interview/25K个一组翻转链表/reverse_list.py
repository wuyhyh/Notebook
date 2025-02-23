class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


class Solution:
    def reverseKGroup(self, head: ListNode, k: int) -> ListNode:
        # 边界条件处理
        if not head or k == 1:
            return head

        # 计算链表长度
        def get_length(head):
            length = 0
            while head:
                length += 1
                head = head.next
            return length

        # 翻转链表的辅助函数
        def reverse_linked_list(head, k):
            prev, curr = None, head
            while k:
                next_node = curr.next
                curr.next = prev
                prev = curr
                curr = next_node
                k -= 1
            return prev, head

        # 获取链表的长度
        length = get_length(head)
        dummy = ListNode(0)
        dummy.next = head
        group_prev = dummy

        while length >= k:
            group_head = group_prev.next
            group_tail = group_head
            for _ in range(k - 1):
                group_tail = group_tail.next
            next_group = group_tail.next
            # 反转当前 k 个节点
            group_tail.next = None
            reversed_head, reversed_tail = reverse_linked_list(group_head, k)

            # 将反转后的链表连接到前后链表
            group_prev.next = reversed_head
            group_head.next = next_group
            group_prev = group_head

            length -= k

        return dummy.next
