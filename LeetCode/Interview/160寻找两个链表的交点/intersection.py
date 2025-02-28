class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


class Solution:
    def intersection(self, headA: ListNode, headB: ListNode) -> ListNode:
        if not headA or not headB:
            return None

        a, b = headA, headB

        while a != b:
            a = headB if a is None else a.next
            b = headA if b is None else b.next

        return a


if __name__ == '__main__':
    a1, a2, a3 = ListNode(1), ListNode(2), ListNode(3)
    b1 = ListNode(4)
    c1, c2, c3 = ListNode(5), ListNode(6), ListNode(7)

    a1.next, a2.next, a3.next = a2, a3, c1
    b1.next = c1
    c1.next, c2.next = c2, c3

    print(Solution().intersection(a1, b1).val)
