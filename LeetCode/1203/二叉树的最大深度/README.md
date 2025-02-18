LeetCode 第104题：“二叉树的最大深度”（**Maximum Depth of Binary Tree**）要求我们返回给定二叉树的最大深度。二叉树的深度是指从根节点到最远叶子节点的最长路径上的节点数。

### 思路：
1. **递归**：最直接的思路是通过递归计算二叉树的深度。每个节点的深度等于它左右子树的最大深度加一。即：
   \[
   \text{Depth} = 1 + \max(\text{Left Subtree Depth}, \text{Right Subtree Depth})
   \]
2. **递归终止条件**：如果当前节点为空（`None`），则返回深度为0。
3. **树的最大深度**：递归遍历整棵树，返回根节点的最大深度。

### 代码实现：

```python
class Solution(object):
    def maxDepth(self, root):
        """
        :type root: TreeNode
        :rtype: int
        """
        if not root:
            return 0  # 如果当前节点为空，返回深度0
        
        # 递归计算左右子树的深度，并返回较大的一个加1
        left_depth = self.maxDepth(root.left)
        right_depth = self.maxDepth(root.right)
        
        return 1 + max(left_depth, right_depth)
```

### 解释：
1. **递归函数 `maxDepth`**：
    - 对于每个节点，如果它为空，返回深度 `0`。
    - 对于非空节点，递归地计算其左右子树的深度。
    - 返回左右子树深度的最大值加1，表示当前节点的深度。

2. **递归终止条件**：当节点为空时（即 `root` 为 `None`），返回 `0`，因为空树没有深度。

3. **返回值**：每一层递归都返回该节点的深度，最终返回根节点的深度，即整棵树的最大深度。

### 例子：
假设有以下二叉树：
```
    1
   / \
  2   3
 / \
4   5
```

- 对于根节点 `1`，它的左右子树分别是 `2` 和 `3`。
- 对于节点 `2`，它的左右子树分别是 `4` 和 `5`。
- 递归过程中，左右子树的最大深度会逐层返回，最终得出树的最大深度是 `3`（即从根节点到最深叶子节点的路径长度）。

### 时间复杂度：
- **时间复杂度**：\(O(n)\)，其中 `n` 是树的节点数。我们需要遍历每个节点一次。
- **空间复杂度**：\(O(h)\)，其中 `h` 是树的高度。递归的栈空间最多会使用树的高度空间，因此最坏情况下空间复杂度是 \(O(n)\)，最好的情况下（树是平衡的）是 \(O(\log n)\)。

### 非递归解法（层序遍历）：
如果你想使用非递归的方法，可以考虑层序遍历（即广度优先遍历，BFS），通过逐层遍历树来计算最大深度。

```python
from collections import deque

class Solution(object):
    def maxDepth(self, root):
        """
        :type root: TreeNode
        :rtype: int
        """
        if not root:
            return 0
        
        queue = deque([root])  # 使用队列进行层序遍历
        depth = 0
        
        while queue:
            # 当前层的节点数
            level_size = len(queue)
            for _ in range(level_size):
                node = queue.popleft()
                if node.left:
                    queue.append(node.left)
                if node.right:
                    queue.append(node.right)
            # 每遍历完一层，深度加1
            depth += 1
        
        return depth
```

### 解释：
- 使用队列 `queue` 来进行层序遍历，每次处理完一层，深度加1。
- 如果当前节点有左子树和右子树，将它们添加到队列中。
- 直到队列为空为止。

### 时间复杂度：
- **时间复杂度**：\(O(n)\)，其中 `n` 是树的节点数。每个节点被访问一次。
- **空间复杂度**：\(O(n)\)，最坏情况下队列中会存储整棵树的节点（例如完全二叉树）。

总结：
- **递归解法**：简单直观，适用于大多数情况，时间和空间复杂度都为 \(O(n)\)。
- **非递归解法**（BFS）：适用于不想使用递归栈的情况，空间复杂度是 \(O(n)\)，适用于大树。

这两种方法都是有效的，你可以根据需要选择其中一种。
