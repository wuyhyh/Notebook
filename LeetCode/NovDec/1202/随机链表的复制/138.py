# Definition for a Node.
class Node:
    def __init__(self, val=0, next=None, random=None):
        self.val = val
        self.next = next
        self.random = random

def copyRandomList(head: Node) -> Node:
    if not head:
        return None

    # 第一步：复制节点并将新节点插入到原节点后面
    current = head
    while current:
        new_node = Node(current.val)
        new_node.next = current.next
        current.next = new_node
        current = new_node.next

    # 第二步：设置每个新节点的 random 指针
    current = head
    while current:
        if current.random:
            current.next.random = current.random.next
        current = current.next.next

    # 第三步：拆分链表，恢复原链表并提取新链表
    original = head
    copy = head.next
    new_head = head.next
    while original:
        original.next = original.next.next
        if copy.next:
            copy.next = copy.next.next
            copy = copy.next
        original = original.next

    return new_head
