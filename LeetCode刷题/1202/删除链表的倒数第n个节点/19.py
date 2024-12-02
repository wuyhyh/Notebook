# Definition for singly-linked list.
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def removeNthFromEnd(head: ListNode, n: int) -> ListNode:
    # 创建一个虚拟头节点，方便删除头节点的情况
    dummy = ListNode(0)
    dummy.next = head
    fast = slow = dummy

    # 让fast指针先走n步
    for _ in range(n):
        fast = fast.next

    # 然后fast和slow一起走，直到fast到达链表末尾
    while fast.next:
        fast = fast.next
        slow = slow.next

    # 删除倒数第n个节点
    slow.next = slow.next.next

    return dummy.next
