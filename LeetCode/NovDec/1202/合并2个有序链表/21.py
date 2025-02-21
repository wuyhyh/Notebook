# Definition for singly-linked list.
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def mergeTwoLists(l1: ListNode, l2: ListNode) -> ListNode:
    # 创建一个虚拟头节点
    dummy = ListNode()
    current = dummy

    # 合并两个链表
    while l1 and l2:
        if l1.val <= l2.val:
            current.next = l1
            l1 = l1.next
        else:
            current.next = l2
            l2 = l2.next
        current = current.next

    # 连接剩余的部分
    if l1:
        current.next = l1
    if l2:
        current.next = l2

    # 返回合并后的链表
    return dummy.next
