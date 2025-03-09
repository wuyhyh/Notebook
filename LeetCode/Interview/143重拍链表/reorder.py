class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


class Solution:
    def reorder(self, head: ListNode) -> None:
        # 使用快慢指针找到链表的中点
        # 反转后半部分的链表
        # 交替合并两个链表
        if not head or not head.next:
            return

        slow, fast = head, head
        while fast and fast.next:
            fast = fast.next.next
            slow = slow.next

        # 反转后半部分
        prev, curr = None, slow.next
        slow.next = None  # 断开链表
        while curr:
            temp = curr.next
            curr.next = prev
            prev = curr
            curr = temp

        # 合并链表
        first, second = head, prev
        while second:
            temp1, temp2 = first.next, second.next
            first.next = second
            second.next = temp1
            first, second = temp1, temp2
