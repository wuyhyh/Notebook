LeetCode 第226题：“翻转二叉树”（**Invert Binary Tree**）要求我们翻转给定的二叉树。翻转一个二叉树就是交换每个节点的左右子树。

### 思路：
1. **递归解法**：我们可以使用递归的方法，遍历每一个节点并交换它的左右子树。
2. **迭代解法（BFS 或 DFS）**：也可以使用迭代方法，通过栈或队列来逐层或逐深度遍历树，交换每个节点的左右子树。

这里我们首先介绍递归解法，然后再讲解迭代解法。

### 1. 递归解法：

递归的基本思路是，遍历树的每个节点，然后交换其左右子节点。递归终止条件是当前节点为空（即 `None`）。

#### 代码实现：

```python
class Solution(object):
    def invertTree(self, root):
        """
        :type root: TreeNode
        :rtype: TreeNode
        """
        # 基本情况：如果节点为空，返回 None
        if not root:
            return None
        
        # 递归交换左右子树
        root.left, root.right = root.right, root.left
        
        # 递归地翻转左右子树
        self.invertTree(root.left)
        self.invertTree(root.right)
        
        return root
```

#### 解释：
- 递归函数 `invertTree` 接收一个节点 `root`，如果 `root` 是空节点（即 `None`），则直接返回 `None`。
- 否则，交换当前节点的左子树和右子树。
- 然后递归地调用 `invertTree` 来翻转左子树和右子树。
- 最终返回翻转后的树的根节点。

#### 示例：
给定二叉树：
```
    4
   / \
  2   7
 / \ / \
1  3 6  9
```

翻转后的树应该是：
```
    4
   / \
  7   2
 / \ / \
9  6 3  1
```

### 2. 迭代解法（使用队列进行层序遍历）：

我们也可以使用迭代的方法，通过层序遍历（广度优先遍历）来逐个交换节点的左右子树。

#### 代码实现：

```python
from collections import deque

class Solution(object):
    def invertTree(self, root):
        """
        :type root: TreeNode
        :rtype: TreeNode
        """
        if not root:
            return None
        
        # 使用队列进行层序遍历
        queue = deque([root])
        
        while queue:
            node = queue.popleft()
            
            # 交换当前节点的左右子树
            node.left, node.right = node.right, node.left
            
            # 如果左子节点存在，将左子节点加入队列
            if node.left:
                queue.append(node.left)
            # 如果右子节点存在，将右子节点加入队列
            if node.right:
                queue.append(node.right)
        
        return root
```

#### 解释：
- 使用一个队列来实现层序遍历，从根节点开始。
- 对于每个节点，交换它的左右子树。
- 然后将该节点的左右子节点（如果有的话）加入队列中，继续遍历。
- 最终返回翻转后的树的根节点。

### 时间复杂度：
- **递归解法**：时间复杂度是 \(O(n)\)，其中 `n` 是树的节点数。每个节点都会被访问一次。
- **迭代解法**：时间复杂度同样是 \(O(n)\)，每个节点也会被访问一次。

### 空间复杂度：
- **递归解法**：空间复杂度是 \(O(h)\)，其中 `h` 是树的高度。最坏情况下，递归栈的深度是树的高度。
- **迭代解法**：空间复杂度是 \(O(n)\)，因为队列中最多存储树的所有节点（最坏情况下是完全二叉树）。

### 总结：
- **递归解法**：简洁且直观，适用于较小的树。时间复杂度和空间复杂度都是 \(O(n)\)，但空间复杂度取决于树的高度。
- **迭代解法**：避免了递归栈的使用，适用于较大的树。时间复杂度和空间复杂度也是 \(O(n)\)，但空间复杂度受限于队列的大小。

这两种方法都可以有效地解决问题，通常根据个人习惯或具体情况选择。
