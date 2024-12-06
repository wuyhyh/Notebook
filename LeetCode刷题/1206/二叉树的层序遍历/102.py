from collections import deque

class Solution(object):
    def levelOrder(self, root):
        """
        :type root: TreeNode
        :rtype: List[List[int]]
        """
        if not root:
            return []  # 如果树为空，返回空列表

        result = []  # 用来存储每一层的节点值
        queue = deque([root])  # 队列初始化，存储当前层的节点

        while queue:
            level_values = []  # 当前层的节点值
            level_size = len(queue)  # 当前层的节点数量

            # 逐个处理当前层的节点
            for _ in range(level_size):
                node = queue.popleft()  # 弹出队列中的一个节点
                level_values.append(node.val)  # 将当前节点的值加入当前层的列表

                # 如果当前节点有左子节点，加入队列
                if node.left:
                    queue.append(node.left)
                # 如果当前节点有右子节点，加入队列
                if node.right:
                    queue.append(node.right)

            result.append(level_values)  # 将当前层的节点值加入结果列表

        return result
