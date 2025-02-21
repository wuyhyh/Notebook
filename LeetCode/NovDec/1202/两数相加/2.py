# Definition for singly-linked list.
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def addTwoNumbers(l1: ListNode, l2: ListNode) -> ListNode:
    # 创建一个虚拟头节点
    dummy = ListNode()
    current = dummy
    carry = 0

    # 遍历两个链表
    while l1 or l2 or carry:
        # 获取当前位的值，若链表为空，则值为0
        val1 = l1.val if l1 else 0
        val2 = l2.val if l2 else 0

        # 计算当前位的和以及新的进位
        total = val1 + val2 + carry
        carry = total // 10  # 更新进位
        current.next = ListNode(total % 10)  # 当前位的值
        current = current.next

        # 移动指针
        if l1:
            l1 = l1.next
        if l2:
            l2 = l2.next

    return dummy.next
