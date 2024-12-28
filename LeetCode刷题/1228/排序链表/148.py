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
