class Solution(object):
    def rightSideView(self, root):
        """
        :type root: TreeNode
        :rtype: List[int]
        """
        result = []

        def dfs(node, depth):
            if not node:
                return

            # 如果当前深度没有记录节点，添加到结果
            if depth == len(result):
                result.append(node.val)

            # 优先遍历右子树，再遍历左子树
            dfs(node.right, depth + 1)
            dfs(node.left, depth + 1)

        dfs(root, 0)
        return result
