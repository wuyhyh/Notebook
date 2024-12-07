
class Solution(object):
    def isValidBST(self, root):
        """
        :type root: TreeNode
        :rtype: bool
        """
        def validate(node, min_val, max_val):
            # 空节点默认是合法的
            if not node:
                return True

            # 当前节点值必须在 (min_val, max_val) 范围内
            if not (min_val < node.val < max_val):
                return False

            # 递归验证左右子树
            return (validate(node.left, min_val, node.val) and
                    validate(node.right, node.val, max_val))

        # 初始范围是 (-∞, +∞)
        return validate(root, float('-inf'), float('inf'))
