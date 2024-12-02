# Definition for singly-linked list.
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def hasCycle(head: ListNode) -> bool:
    if not head:
        return False

    slow, fast = head, head

    while fast and fast.next:
        slow = slow.next        # 慢指针走一步
        fast = fast.next.next   # 快指针走两步

        if slow == fast:        # 如果快慢指针相遇，说明有环
            return True

    return False  # 如果快指针指向 None，说明没有环
