from collections import deque
from typing import Optional, List


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


class Solution:
    def right_side_view(self, root: Optional[TreeNode]) -> List[int]:
        if not root:
            return []

        result = []  # 存储右视图的节点值
        queue = deque([root])  # 使用队列进行层序遍历

        while queue:
            level_size = len(queue)  # 当前层的节点数量

            for i in range(level_size):
                node = queue.popleft()  # 取出当前层的节点
                if i == level_size - 1:
                    result.append(node.val)  # 记录每层的最后一个节点

                # 根左右的中序遍历，保证最右侧节点被最后访问
                if node.left:
                    queue.append(node.left)
                if node.right:
                    queue.append(node.right)

        return result


# 测试代码
if __name__ == '__main__':
    root = TreeNode(1)
    root.left = TreeNode(2)
    root.right = TreeNode(3)
    root.left.left = TreeNode(5)
    root.right.right = TreeNode(4)

    print("Right side view:", Solution().right_side_view(root))
