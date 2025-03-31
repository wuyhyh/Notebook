from typing import List


class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


class Solution:
    def has_cycle(self, head: ListNode) -> bool:
        # 使用快慢指针，如果相遇说明存在环
        slow = head
        fast = head

        while fast and fast.next:
            slow = slow.next
            fast = fast.next.next
            if slow == fast:
                return True

        return False


def create_linked_list_with_cycle(values, pos):
    if not values:
        return None

    nodes = [ListNode(val) for val in values]
    for i in range(len(nodes) - 1):
        nodes[i].next = nodes[i + 1]

    if pos != -1:
        nodes[-1].next = nodes[pos]  # 创建环

    return nodes[0]


if __name__ == '__main__':
    head = create_linked_list_with_cycle([3, 2, 0, -4], 1)
    solution = Solution()
    print(solution.has_cycle(head))
