LeetCode 第101题：“对称二叉树”（**Symmetric Tree**）要求我们判断一个二叉树是否是对称的，即树的左右子树是否是镜像对称的。

### 思路：
1. **对称的定义**：一个二叉树是对称的，当它的左子树和右子树是镜像对称的。具体来说：
    - 根节点的左子树和右子树相同；
    - 左子树的左子树与右子树的右子树相同；
    - 左子树的右子树与右子树的左子树相同。

2. **递归解法**：
    - 通过递归函数比较树的左右子树是否镜像对称。
    - 递归的比较条件是：如果左子树的值等于右子树的值，并且左子树的左子树与右子树的右子树相对称，左子树的右子树与右子树的左子树相对称，那么这两棵子树是对称的。

3. **迭代解法**（可选）：
    - 我们可以使用队列或栈来模拟递归的过程，逐层比较树的左右子树是否对称。

### 1. 递归解法

递归解法的基本思想是使用一个辅助函数来比较两个节点是否镜像对称。对于每一对节点：
- 它们的值必须相同；
- 它们的左右子树必须相互镜像。

#### 代码实现：

```python
class Solution(object):
    def isSymmetric(self, root):
        """
        :type root: TreeNode
        :rtype: bool
        """
        # 如果根节点为空，认为是对称的
        if not root:
            return True
        
        # 定义一个递归函数来判断左右子树是否对称
        def isMirror(t1, t2):
            if not t1 and not t2:
                return True  # 两个节点都为空，对称
            if not t1 or not t2:
                return False  # 一个为空，一个不为空，不对称
            return (t1.val == t2.val) and isMirror(t1.left, t2.right) and isMirror(t1.right, t2.left)
        
        # 从根节点开始比较左右子树
        return isMirror(root.left, root.right)
```

#### 解释：
- **`isSymmetric`** 方法：首先判断根节点是否为空，如果为空，则返回 `True`（空树是对称的）。然后调用辅助函数 `isMirror` 来比较左右子树。
- **`isMirror`** 方法：递归地判断两棵树是否是镜像对称的。递归的终止条件是：当两个节点都为空时返回 `True`，如果其中一个为空，另一个不为空时返回 `False`。如果当前节点的值相同且它们的左右子树符合镜像对称的条件，则返回 `True`。

### 2. 迭代解法（使用队列）

我们可以使用队列来实现广度优先遍历（BFS），逐层比较树的左右子树是否对称。对于每一对节点，我们将它们的左右子树放入队列中，继续比较它们的值。

#### 代码实现：

```python
from collections import deque

class Solution(object):
    def isSymmetric(self, root):
        """
        :type root: TreeNode
        :rtype: bool
        """
        if not root:
            return True
        
        queue = deque([root.left, root.right])  # 从根节点的左右子树开始
        while queue:
            t1, t2 = queue.popleft(), queue.popleft()
            
            # 如果两个节点都为空，则继续遍历
            if not t1 and not t2:
                continue
            # 如果只有一个为空，或者它们的值不同，则不是对称的
            if not t1 or not t2 or t1.val != t2.val:
                return False
            
            # 将子节点放入队列，左右子树要互换顺序
            queue.append(t1.left)
            queue.append(t2.right)
            queue.append(t1.right)
            queue.append(t2.left)
        
        return True
```

#### 解释：
- 使用队列来保存节点对，每次从队列中取出两个节点进行比较。
- 对于每一对节点，如果它们都为空，则跳过；如果只有一个为空，或者它们的值不同，则返回 `False`（不是对称的）。
- 如果节点值相同，则将它们的子节点按镜像顺序（左子树与右子树互换）加入队列。
- 直到队列为空，说明所有节点都符合镜像对称的条件，返回 `True`。

### 3. 时间和空间复杂度分析：
- **递归解法**：
    - **时间复杂度**：\(O(n)\)，其中 `n` 是树的节点数。我们需要遍历每个节点一次。
    - **空间复杂度**：\(O(h)\)，其中 `h` 是树的高度。递归栈的空间复杂度是树的高度，最坏情况下为 \(O(n)\)（例如树是链状的），最好的情况下为 \(O(\log n)\)（树是平衡的）。

- **迭代解法**：
    - **时间复杂度**：\(O(n)\)，我们仍然需要遍历每个节点一次。
    - **空间复杂度**：\(O(n)\)，队列中最多会存储树的一层节点。最坏情况下（完全二叉树），队列中会有 \(n/2\) 个节点。

### 总结：
- **递归解法**：简洁直观，时间和空间复杂度为 \(O(n)\)，适合树的结构较小或平衡的情况。
- **迭代解法**：使用队列避免了递归栈，适合避免递归深度过大的情况，空间复杂度为 \(O(n)\)。

两种解法都可以有效地解决问题，可以根据需求选择合适的实现方式。