# Definition for singly-linked list.
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def reverseKGroup(head: ListNode, k: int) -> ListNode:
    # 检查链表长度是否至少为 k
    def has_k_nodes(node, k):
        count = 0
        while node and count < k:
            node = node.next
            count += 1
        return count == k

    # 翻转链表的一部分
    def reverse_linked_list(start, k):
        prev = None
        cur = start
        while k > 0:
            next_node = cur.next
            cur.next = prev
            prev = cur
            cur = next_node
            k -= 1
        return prev, start  # 返回新的头节点和尾节点

    # 处理链表
    dummy = ListNode(0)
    dummy.next = head
    group_prev = dummy  # group_prev 用来连接翻转后的部分

    while head:
        if has_k_nodes(head, k):
            # 如果剩余的节点大于等于 k，则翻转这 k 个节点
            group_start = head
            group_end = head
            for _ in range(k - 1):
                group_end = group_end.next

            # 保存下一个部分
            next_group = group_end.next
            # 翻转当前 k 个节点
            new_head, new_tail = reverse_linked_list(group_start, k)

            # 连接翻转后的部分
            group_prev.next = new_head
            group_start.next = next_group
            group_prev = group_start
            head = next_group
        else:
            # 如果剩余节点不足 k，直接返回
            break

    return dummy.next
