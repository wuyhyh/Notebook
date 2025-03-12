class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


class Solution:
    def deleteDuplicates(self, head: ListNode) -> ListNode:
        # 创建虚拟头结点
        dummy = ListNode(0)
        dummy.next = head
        prev = dummy  # 指向第一个不重复的节点

        while head:
            # 如果当前节点与下一个节点值相同，应该被去除
            if head.next and head.val == head.next.val:
                # 跳过相同的节点
                while head.next and head.val == head.next.val:
                    head = head.next
                # 更新不重复的节点
                prev.next = head.next
            else:
                prev = prev.next
            head = head.next

        return dummy.next


# 测试代码
def print_list(head):
    values = []
    while head:
        values.append(head.val)
        head = head.next
    print(values)


if __name__ == '__main__':
    head = ListNode(1, ListNode(1, ListNode(1, ListNode(2, ListNode(3)))))
    print_list(head)
    solution = Solution()
    head = solution.deleteDuplicates(head)
    print_list(head)
