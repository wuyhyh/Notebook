class TreeNode(object):
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

class Solution(object):
    def sortedArrayToBST(self, nums):
        """
        :type nums: List[int]
        :rtype: TreeNode
        """
        # 边界条件：如果数组为空，返回 None
        if not nums:
            return None

        # 选择中间元素作为根节点
        mid = len(nums) // 2
        root = TreeNode(nums[mid])

        # 递归构造左子树和右子树
        root.left = self.sortedArrayToBST(nums[:mid])  # 左部分构造左子树
        root.right = self.sortedArrayToBST(nums[mid+1:])  # 右部分构造右子树

        return root
