# Definition for singly-linked list.
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def reverseList(head: ListNode) -> ListNode:
    prev = None
    curr = head

    while curr:
        next_node = curr.next   # 暂存当前节点的下一个节点
        curr.next = prev       # 反转当前节点的指向
        prev = curr            # prev 移动到当前节点
        curr = next_node       # curr 移动到下一个节点

    return prev  # prev 最终指向新链表的头节点
