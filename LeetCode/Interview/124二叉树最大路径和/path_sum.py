class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


class Solution:
    def max_path_sum(self, root: TreeNode) -> int:
        self.max_sum = float('-inf')  # 初始化最大路径为负无穷

        def dfs(node):  # 递归计算从当前节点出发的最大单边贡献值
            if node is None:  # 递归终止条件，空节点返回0
                return 0

            left_max = max(dfs(node.left), 0)  # 负数的话就放弃这条路，贡献值为0
            right_max = max(dfs(node.right), 0)

            # 计算当前节点作为根节点的路径的最大路径和
            curr_sum = node.val + left_max + right_max

            # 更新全局最大路径和
            self.max_sum = max(self.max_sum, curr_sum)

            # 返回当前节点向上的单边贡献值，用于其父节点的计算
            return max(left_max, right_max) + node.val

        # 主函数，计算最大路径和
        dfs(root)
        return self.max_sum


# 测试
if __name__ == '__main__':
    root = TreeNode(1)
    root.left = TreeNode(2)
    root.right = TreeNode(3)
    s = Solution()
    print(s.max_path_sum(root))

    root2 = TreeNode(-10)
    root2.left = TreeNode(9)
    root2.right = TreeNode(20)
    root2.right.left = TreeNode(15)
    root2.right.right = TreeNode(7)
    print(s.max_path_sum(root2))

    root3 = TreeNode(-3)
    print(s.max_path_sum(root3))
