from typing import Optional


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


class Solution:
    def serialize(self, root: Optional[TreeNode]) -> str:
        def dfs(node: TreeNode):
            if not node:
                return "null"
            # 前序遍历拼接字符串
            left = dfs(node.left)
            right = dfs(node.right)
            return f"{node.val},{left},{right}"

        return dfs(root)

    def deserialize(self, date: str) -> TreeNode:
        # 将字符转换为列表，方便递归处理
        values = date.split(',')
        self.index = 0  # 用于跟踪当前解析位置

        def dfs():
            if values[self.index] == 'null':
                self.index += 1
                return None

            node = TreeNode(int(values[self.index]))
            self.index += 1
            node.left = dfs()
            node.right = dfs()
            return node

        return dfs()


def print_tree_preorder(root: TreeNode):
    if not root:
        return ["null"]
    return [str(root.val)] + print_tree_preorder(root.left) + print_tree_preorder(root.right)


if __name__ == "__main__":
    solution = Solution()
    root = TreeNode(1)
    root.left = TreeNode(2)
    root.right = TreeNode(3)
    root.right.left = TreeNode(4)
    root.right.right = TreeNode(5)

    print(solution.serialize(root))

    # 序列化
    data = solution.serialize(root)
    print(data)

    # 反序列化
    new_root = solution.deserialize(data)
    print(print_tree_preorder(new_root))
