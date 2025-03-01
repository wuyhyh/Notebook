class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


class Solution:
    def sortList(self, head: ListNode) -> ListNode:
        # 递归终止条件
        if head is None or head.next is None:
            return head

        # 1. 使用快慢指针找到链表的中点
        slow, fast = head, head.next
        while fast and fast.next:
            slow = slow.next
            fast = fast.next.next

        # 2. 断开链表
        mid = slow.next
        slow.next = None

        # 3. 递归对左右两部分进行排序
        left = self.sortList(head)
        right = self.sortList(mid)

        # 4. 归并两个有序链表
        return self.mergeLists(left, right)

    def mergeLists(self, headA, headB):
        dummy = ListNode(0)
        cur = dummy

        # 决定下一个节点
        while headA and headB:
            if headA.val <= headB.val:
                cur.next = headA
                headA = headA.next
            else:
                cur.next = headB
                headB = headB.next
            cur = cur.next

        # 处理剩余节点
        cur.next = headA if headA else headB

        return dummy.next
