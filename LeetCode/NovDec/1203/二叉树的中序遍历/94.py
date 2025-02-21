class Solution(object):
    def inorderTraversal(self, root):
        """
        :type root: TreeNode
        :rtype: List[int]
        """
        result = []

        # 中序遍历的递归函数
        def dfs(node):
            if not node:
                return
            # 先遍历左子树
            dfs(node.left)
            # 然后访问根节点
            result.append(node.val)
            # 最后遍历右子树
            dfs(node.right)

        dfs(root)
        return result
