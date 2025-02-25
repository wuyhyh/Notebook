from width import Solution, TreeNode


def test_solution():
    root1 = TreeNode(1)
    root1.left = TreeNode(3)
    root1.right = TreeNode(2)
    root1.left.left = TreeNode(5)
    root1.left.right = TreeNode(3)
    root1.right.right = TreeNode(9)

    solution = Solution()
    print("test case 1, max_width = ", solution.widthOfBinaryTree(root1))


test_solution()
