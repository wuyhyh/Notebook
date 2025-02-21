class TreeNode(object):
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

class Solution(object):
    def pathSum(self, root, sum):
        """
        :type root: TreeNode
        :type sum: int
        :rtype: int
        """
        # 记录当前路径和出现的次数
        path_count = {0: 1}  # 初始化，表示从根节点开始的路径和为0的路径有1条
        return self.dfs(root, sum, 0, path_count)

    def dfs(self, node, target, current_sum, path_count):
        if not node:
            return 0

        # 更新当前路径的和
        current_sum += node.val

        # 计算当前路径中有多少个子路径的和为target
        result = path_count.get(current_sum - target, 0)

        # 更新哈希表：增加当前路径和出现的次数
        path_count[current_sum] = path_count.get(current_sum, 0) + 1

        # 递归遍历左右子树
        result += self.dfs(node.left, target, current_sum, path_count)
        result += self.dfs(node.right, target, current_sum, path_count)

        # 回溯，移除当前节点的路径和
        path_count[current_sum] -= 1

        return result
