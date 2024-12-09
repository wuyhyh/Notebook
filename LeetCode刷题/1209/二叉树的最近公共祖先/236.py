class TreeNode(object):
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

class Solution(object):
    def lowestCommonAncestor(self, root, p, q):
        """
        :type root: TreeNode
        :type p: TreeNode
        :type q: TreeNode
        :rtype: TreeNode
        """
        # 如果当前节点为空，或者当前节点就是p或q，则返回当前节点
        if not root or root == p or root == q:
            return root

        # 递归查找左右子树
        left = self.lowestCommonAncestor(root.left, p, q)
        right = self.lowestCommonAncestor(root.right, p, q)

        # 如果左右子树都返回非空，则说明p和q分别在当前节点的左右子树
        if left and right:
            return root

        # 否则返回非空的那个子树节点
        return left if left else right