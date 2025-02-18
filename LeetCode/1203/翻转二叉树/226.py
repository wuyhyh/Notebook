class Solution(object):
    def invertTree(self, root):
        """
        :type root: TreeNode
        :rtype: TreeNode
        """
        # 基本情况：如果节点为空，返回 None
        if not root:
            return None

        # 递归交换左右子树
        root.left, root.right = root.right, root.left

        # 递归地翻转左右子树
        self.invertTree(root.left)
        self.invertTree(root.right)

        return root
