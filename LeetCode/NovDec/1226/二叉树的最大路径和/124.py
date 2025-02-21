class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def maxPathSum(root):
    # 用于记录全局最大路径和
    max_sum = float('-inf')

    # 定义递归函数，返回从当前节点出发的最大路径和
    def helper(node):
        nonlocal max_sum
        if not node:
            return 0

        # 计算左子树和右子树的最大路径和，负数要取0，因为不能让路径和变差
        left = max(helper(node.left), 0)  # 左子树最大路径和
        right = max(helper(node.right), 0)  # 右子树最大路径和

        # 更新全局最大路径和
        max_sum = max(max_sum, node.val + left + right)

        # 返回当前节点的最大贡献（即该节点的值 + 左右子树中较大的路径）
        return node.val + max(left, right)

    # 启动递归
    helper(root)

    return max_sum
