class Solution(object):
    def kthSmallest(self, root, k):
        """
        :type root: TreeNode
        :type k: int
        :rtype: int
        """
        self.count = 0  # 当前访问的节点计数
        self.result = None  # 第 k 小的节点值

        def inorder(node):
            if not node or self.result is not None:
                return

            # 递归遍历左子树
            inorder(node.left)

            # 访问当前节点
            self.count += 1
            if self.count == k:
                self.result = node.val
                return

            # 递归遍历右子树
            inorder(node.right)

        inorder(root)
        return self.result
