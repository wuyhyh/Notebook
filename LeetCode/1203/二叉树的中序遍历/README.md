LeetCode 第94题是“二叉树的中序遍历”（**Binary Tree Inorder Traversal**），要求你返回一个二叉树的中序遍历结果。

### 中序遍历的定义：
- **中序遍历**的顺序是：**左子树 -> 根节点 -> 右子树**。

### 思路：
1. 对于每一个节点，首先访问它的左子树，然后访问节点本身，最后访问右子树。
2. 需要考虑三种解法：递归、迭代、Morris 遍历。

我们先来看递归和迭代两种常见的解法。

### 1. 递归解法

递归解法是最简单的，它直接按照中序遍历的定义进行。通过递归遍历左子树、根节点和右子树。

#### 代码实现：

```python
class Solution(object):
    def inorderTraversal(self, root):
        """
        :type root: TreeNode
        :rtype: List[int]
        """
        result = []
        
        # 中序遍历的递归函数
        def dfs(node):
            if not node:
                return
            # 先遍历左子树
            dfs(node.left)
            # 然后访问根节点
            result.append(node.val)
            # 最后遍历右子树
            dfs(node.right)
        
        dfs(root)
        return result
```

#### 解释：
- 我们定义了一个 `dfs` 函数，它在遍历每个节点时，按照中序遍历的顺序（左 -> 根 -> 右）依次进行。
- 如果节点为空（即递归的终止条件），我们就直接返回。
- 每遍历到一个节点，我们就将它的值添加到结果列表 `result` 中。
- 最后返回 `result` 列表，就是中序遍历的结果。

### 2. 迭代解法（使用栈）

迭代方法则使用栈来模拟递归过程。通过栈，我们可以模拟树的深度优先遍历，来达到中序遍历的目的。

#### 代码实现：

```python
class Solution(object):
    def inorderTraversal(self, root):
        """
        :type root: TreeNode
        :rtype: List[int]
        """
        result = []
        stack = []
        current = root
        
        while current or stack:
            # 将当前节点及其左子树压入栈
            while current:
                stack.append(current)
                current = current.left
            
            # 弹出栈顶元素，访问它
            current = stack.pop()
            result.append(current.val)
            
            # 转向右子树
            current = current.right
        
        return result
```

#### 解释：
- 我们使用栈来模拟递归过程。首先将根节点及其左子树压入栈中，直到我们到达最左边的节点。
- 然后，弹出栈顶元素，访问该节点并将它的值添加到结果列表中。
- 接着，我们转向右子树，重复这个过程，直到栈为空且当前节点为 `None`。

### 3. Morris 遍历（不使用栈或递归）

Morris 遍历是一种空间复杂度为 \(O(1)\) 的中序遍历算法，它通过在树上做线索化，避免了栈的使用。

这里简要描述这个方法，但代码会相对复杂一些。如果你感兴趣，之后可以深入了解。

### 总结：
- **递归解法**：简单直观，代码清晰，空间复杂度 \(O(h)\)（其中 \(h\) 是树的高度，最坏情况下为 \(O(n)\)）。
- **迭代解法**：通过栈模拟递归，空间复杂度也是 \(O(h)\)。
- **Morris 遍历**：空间复杂度是 \(O(1)\)，但实现起来相对复杂。

你可以根据自己的需求选择合适的解法。最常用的是递归和迭代解法。
