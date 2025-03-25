from typing import Optional, List


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


class Solution:
    def diameter_of_bt(self, root: TreeNode) -> int:
        # 记录最大直径
        self.max_diameter = 0

        def dfs(node):
            if not node:
                return 0

            left_depth = dfs(node.left)
            right_depth = dfs(node.right)
            self.max_diameter = max(self.max_diameter, left_depth + right_depth)  # 当前节点的直径等于left+right
            return max(left_depth, right_depth) + 1  # 当前root的最大深度

        dfs(root)
        return self.max_diameter


# 从List构造二叉树
def build_tree_from_list(values: List[int]) -> TreeNode:
    if not values:
        return None
    from collections import deque
    root = TreeNode(values[0])
    queue = deque([root])
    index = 1
    while queue and index < len(values):
        node = queue.popleft()
        if values[index] is not None:
            node.left = TreeNode(values[index])
            queue.append(node.left)
        index = index + 1
        if index < len(values) and values[index] is not None:
            node.right = TreeNode(values[index])
            queue.append(node.right)
        index = index + 1

    return root


if __name__ == '__main__':
    values = [1, 2, 3, 4, 5]
    root = build_tree_from_list(values)
    solution = Solution()
    result = solution.diameter_of_bt(root)
    print(result)
