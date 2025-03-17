class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


class Solution:
    def is_sub_structure(self, A: TreeNode, B: TreeNode) -> bool:
        if not A or not B:  # 任何一棵树为空，返回false
            return False

        # 以节点A为起点，检查是否匹配B
        def match(A, B):
            if not B:
                return True
            if not A or A.val != B.val:
                return False
            return match(A.left, B.left) and match(A.right, B.right)

        # 以节点A或者A的左右子树进行匹配
        return match(A, B) or self.is_sub_structure(A.left, B) or self.is_sub_structure(A.right, B)


if __name__ == '__main__':
    A = TreeNode(3)
    A.left = TreeNode(4)
    A.right = TreeNode(5)
    A.left.left = TreeNode(1)
    A.left.right = TreeNode(2)

    B = TreeNode(4)
    B.left = TreeNode(1)

    solution = Solution()
    print(solution.is_sub_structure(A, B))
