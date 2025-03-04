from collections import deque
from typing import List, Optional


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


class Solution:
    def zigzagLevelOrder(self, root: Optional[TreeNode]) -> List[List[int]]:
        if not root:
            return []  # 如果树为空

        result = []
        queue = deque([root])  # 使用队列实现层序遍历
        left_to_right = True  # 控制遍历方向

        while queue:
            curr_level_size = len(queue)  # 当前层节点数量
            curr_level_nodes = deque()

            # 遍历当前层
            for _ in range(curr_level_size):
                node = queue.popleft()

                # 根据遍历方向构造结果list
                if left_to_right:
                    curr_level_nodes.append(node.val)
                else:
                    curr_level_nodes.appendleft(node.val)

                # 将子节点加入队列，遍历下一层
                if node.left:
                    queue.append(node.left)
                if node.right:
                    queue.append(node.right)

            # 将当前层的结果放入最终结果
            result.append(list(curr_level_nodes))

            # 切换遍历方向
            left_to_right = not left_to_right

        return result


# 测试代码

if __name__ == '__main__':
    root = TreeNode(3)
    root.left = TreeNode(9)
    root.right = TreeNode(20)
    root.right.left = TreeNode(15)
    root.right.right = TreeNode(7)

    sol = Solution()
    print(sol.zigzagLevelOrder(root))
