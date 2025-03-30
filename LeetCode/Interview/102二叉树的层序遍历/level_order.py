from collections import deque
from typing import List


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


class Solution:
    def level_order(self, root: TreeNode) -> List[List[int]]:
        if not root:
            return []

        result = []  # 存放结果
        queue = deque([root])  # 使用队列实现BFS，初始化放入根节点

        while queue:
            level_size = len(queue)
            level = []  # 记录当前节点的值

            for _ in range(level_size):
                node = queue.popleft()
                level.append(node.val)  # visit 节点

                if node.left:  # 将下一层的子节点加入队列
                    queue.append(node.left)
                if node.right:
                    queue.append(node.right)

            result.append(level)

        return result


def build_tree_from_list(values: List) -> TreeNode:
    if not values:
        return None

    root = TreeNode(values[0])
    queue = deque([root])
    index = 1

    while queue and index < len(values):
        node = queue.popleft()
        if values[index] is not None:
            node.left = TreeNode(values[index])
            queue.append(node.left)
        index += 1

        if index < len(values) and values[index] is not None:
            node.right = TreeNode(values[index])
            queue.append(node.right)
        index += 1

    return root


if __name__ == '__main__':
    values = [3, 9, 20, None, None, 15, 7]
    root = build_tree_from_list(values)

    solution = Solution()
    result = solution.level_order(root)
    print(result)
