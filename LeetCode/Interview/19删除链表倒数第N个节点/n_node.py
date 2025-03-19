class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


class Solution:
    def remove_nth_node_from_end(self, head: ListNode, n: int) -> ListNode:
        # 创建一个虚拟头结点
        dummy = ListNode(0)
        dummy.next = head

        # 使用快慢指针，让快指针先走N+1步
        fast = slow = dummy
        for _ in range(n + 1):
            fast = fast.next

        # 快慢指针一起走，直到快指针到达末尾
        while fast:
            fast = fast.next
            slow = slow.next

        # 删除目标节点
        slow.next = slow.next.next

        return dummy.next


def print_list(head):
    result = []
    while head:
        result.append(head.val)
        head = head.next
    print(result)


if __name__ == '__main__':
    head = ListNode(1, ListNode(2, ListNode(3, ListNode(4, ListNode(5)))))
    print_list(head)

    solution = Solution()
    new_head = solution.remove_nth_node_from_end(head, 2)
    print_list(new_head)
