class Solution(object):
    def isSymmetric(self, root):
        """
        :type root: TreeNode
        :rtype: bool
        """
        # 如果根节点为空，认为是对称的
        if not root:
            return True

        # 定义一个递归函数来判断左右子树是否对称
        def isMirror(t1, t2):
            if not t1 and not t2:
                return True  # 两个节点都为空，对称
            if not t1 or not t2:
                return False  # 一个为空，一个不为空，不对称
            return (t1.val == t2.val) and isMirror(t1.left, t2.right) and isMirror(t1.right, t2.left)

        # 从根节点开始比较左右子树
        return isMirror(root.left, root.right)
