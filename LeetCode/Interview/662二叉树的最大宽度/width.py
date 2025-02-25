from collections import deque


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


class Solution:
    def widthOfBinaryTree(self, root: TreeNode) -> int:
        if not root:
            return 0

        # 初始化队列，存储节点及其对应的索引
        queue = deque([(root, 0)])
        max_width = 0

        # 开始 BFS 遍历
        while queue:
            level_length = len(queue)
            level_min = queue[0][1]  # 该层最左节点的索引
            for i in range(level_length):
                node, index = queue.popleft()

                # 记录当前层的宽度
                if node.left:
                    queue.append((node.left, 2 * index))
                if node.right:
                    queue.append((node.right, 2 * index + 1))

            # 计算当前层的宽度
            level_max = queue[-1][1] if queue else index
            max_width = max(max_width, level_max - level_min + 1)

        return max_width
