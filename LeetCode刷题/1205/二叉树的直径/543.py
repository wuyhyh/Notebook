class Solution(object):
    def diameterOfBinaryTree(self, root):
        """
        :type root: TreeNode
        :rtype: int
        """
        self.diameter = 0  # 用于存储最大直径

        # 定义一个递归函数计算深度并更新最大直径
        def depth(node):
            if not node:
                return 0  # 空节点的深度是0

            # 递归计算左右子树的深度
            left_depth = depth(node.left)
            right_depth = depth(node.right)

            # 更新最大直径
            self.diameter = max(self.diameter, left_depth + right_depth)

            # 返回当前节点的深度
            return 1 + max(left_depth, right_depth)

        # 从根节点开始递归计算
        depth(root)

        # 最终返回的是最大直径
        return self.diameter
