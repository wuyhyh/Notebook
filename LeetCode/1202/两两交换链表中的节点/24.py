# Definition for singly-linked list.
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def swapPairs(head: ListNode) -> ListNode:
    # 创建一个虚拟头节点
    dummy = ListNode(0)
    dummy.next = head
    prev = dummy  # prev 用来指向要交换节点的前一个节点

    # 遍历链表
    while head and head.next:
        # 记录两个要交换的节点
        first = head
        second = head.next

        # 交换节点
        prev.next = second  # prev 指向第二个节点
        first.next = second.next  # 第一个节点指向第二个节点之后的节点
        second.next = first  # 第二个节点指向第一个节点

        # 移动 prev 和 head 指针
        prev = first
        head = first.next

    # 返回交换后的链表
    return dummy.next
