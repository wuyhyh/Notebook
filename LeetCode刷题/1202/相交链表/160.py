# Definition for singly-linked list.
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def getIntersectionNode(headA: ListNode, headB: ListNode) -> ListNode:
    # 如果两个链表为空，直接返回 None
    if not headA or not headB:
        return None

    # 定义两个指针
    pA, pB = headA, headB

    # 遍历两个链表
    while pA != pB:
        # 当指针 pA 到达链表 A 的末尾时，将它指向链表 B 的头部
        # 同理，当指针 pB 到达链表 B 的末尾时，将它指向链表 A 的头部
        pA = pA.next if pA else headB
        pB = pB.next if pB else headA

    # 如果有交点，pA 和 pB 会相遇；如果没有交点，pA 和 pB 会同时指向 None
    return pA
