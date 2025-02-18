class Solution(object):
    def flatten(self, root):
        """
        :type root: TreeNode
        :rtype: None Do not return anything, modify root in-place instead.
        """
        if not root:
            return

        # 对右子树和左子树进行递序展张
        self.flatten(root.right)
        self.flatten(root.left)

        # 展张当前节点
        temp = root.right
        root.right = root.left
        root.left = None

        # 将原右子树链接到当前右子树底部
        curr = root
        while curr.right:
            curr = curr.right
        curr.right = temp
