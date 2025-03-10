from typing import List


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


class Solution:
    def buildTree(self, preorder: List[int], inorder: List[int]) -> TreeNode:
        # 如果序列为空，返回None
        if not preorder or not inorder:
            return None

        # 前序遍历的第一个节点是根节点
        root_val = preorder[0]
        root = TreeNode(root_val)

        # 在中序遍历中找到根节点的位置
        root_index = inorder.index(root_val)

        # 递归构建左右子树
        root.left = self.buildTree(preorder[1:root_index + 1], inorder[:root_index])
        root.right = self.buildTree(preorder[root_index + 1:], inorder[root_index + 1:])

        return root


# 层序遍历函数，方便测试
def level_order_traversal(root: TreeNode) -> List[List[int]]:
    if not root:
        return []

    from collections import deque
    queue = deque([root])
    result = []

    while queue:
        node = queue.popleft()
        if node:
            result.append(node.val)
            queue.append(node.left)
            queue.append(node.right)
        else:
            result.append(None)

    # 去除末尾多余的Node
    while result and result[-1] is None:
        result.pop()

    return result


# 测试
if __name__ == "__main__":
    sol = Solution()

    preorder = [3, 9, 20, 15, 7]
    inorder = [9, 3, 15, 20, 7]
    root = sol.buildTree(preorder, inorder)
    print(level_order_traversal(root))
