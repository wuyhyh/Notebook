# Definition for singly-linked list.
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def detectCycle(head: ListNode) -> ListNode:
    if not head or not head.next:
        return None

    slow, fast = head, head

    # 步骤 1: 快慢指针相遇检测环
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next

        if slow == fast:  # 快慢指针相遇，说明有环
            # 步骤 2: 寻找环的入口
            pointer1 = head
            pointer2 = slow

            while pointer1 != pointer2:  # 让两指针一起走，直到它们相遇
                pointer1 = pointer1.next
                pointer2 = pointer2.next

            return pointer1  # 返回环的入口节点

    return None  # 没有环
