class TreeNode(object):
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

class Solution(object):
    def buildTree(self, preorder, inorder):
        """
        :type preorder: List[int]
        :type inorder: List[int]
        :rtype: TreeNode
        """
        if not preorder or not inorder:
            return None

        # 前序遍历的第一个元素是当前树的根节点
        root_val = preorder[0]
        root = TreeNode(root_val)

        # 在中序遍历中找到根节点的位置
        root_index = inorder.index(root_val)

        # 左子树的节点数量为中序遍历中根节点左边的节点数量
        left_size = root_index

        # 构造左子树和右子树
        root.left = self.buildTree(preorder[1:1+left_size], inorder[:root_index])
        root.right = self.buildTree(preorder[1+left_size:], inorder[root_index+1:])

        return root
