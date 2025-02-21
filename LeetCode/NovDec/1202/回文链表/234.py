# Definition for singly-linked list.
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def isPalindrome(head: ListNode) -> bool:
    if not head or not head.next:
        return True

    # 快慢指针找到链表的中点
    slow, fast = head, head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next

    # 反转后半部分链表
    prev = None
    while slow:
        next_node = slow.next
        slow.next = prev
        prev = slow
        slow = next_node

    # 比较前半部分和后半部分
    left, right = head, prev
    while right:  # 只需要比较后半部分
        if left.val != right.val:
            return False
        left = left.next
        right = right.next

    return True
