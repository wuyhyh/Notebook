from typing import List
from collections import deque


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


class Solution:
    def path_sum(self, root: TreeNode, target: int) -> List[List[int]]:
        result = []  # 结果集合
        curr_path = []  # 记录当前路径

        def dfs(node, remaining_sum):
            if not node:
                return

            # 将当前节点加入路径
            curr_path.append(node.val)

            # 检查是否是叶节点，并且符合要求
            if not node.left and not node.right and remaining_sum == node.val:
                result.append(list(curr_path))

            # 递归处理左右子树
            dfs(node.left, remaining_sum - node.val)
            dfs(node.right, remaining_sum - node.val)

            # 回溯
            curr_path.pop()

        # 开始 DFS
        dfs(root, target)
        return result


# 使用列表构造二叉树
def build_tree_from_list(values: List):
    if not values or values[0] is None:
        return None  # 空树

    # 创建根节点
    root = TreeNode(values[0])
    queue = deque([root])
    i = 1

    while i < len(values):
        node = queue.popleft()

        if i < len(values) and values[i] is not None:
            node.left = TreeNode(values[i])
            queue.append(node.left)
        i += 1

        if i < len(values) and values[i] is not None:
            node.right = TreeNode(values[i])
            queue.append(node.right)
        i += 1

    return root


def level_order_traversal(root):
    if not root:
        return

    queue = deque([root])
    result = []
    while queue:
        node = queue.popleft()
        result.append(node.val)
        if node.left:
            queue.append(node.left)
        if node.right:
            queue.append(node.right)

    return result


# 测试
if __name__ == '__main__':
    values = [5, 4, 8, 11, None, 13, 4, 7, 2, None, None, 5, 1]
    root = build_tree_from_list(values)
    print(level_order_traversal(root))  # 输出 [5, 4, 8, 11, None, 13, 4, 7, 2, None, None, 5, 1]

    solution = Solution()
    result = solution.path_sum(root, 22)
    print(result)
