LeetCode 第236题：“二叉树的最近公共祖先”（**Lowest Common Ancestor of a Binary Tree**）要求我们在一棵二叉树中，找到两个节点的最近公共祖先（LCA）。最近公共祖先定义为：对于树中的两个节点 `p` 和 `q`，最近公共祖先是树中同时包含 `p` 和 `q` 的最深的节点。

### **思路分析：**

1. **树的递归性质**：
    - 二叉树的递归特性意味着我们可以通过递归从根节点开始搜索，检查每个节点是否是所求的最近公共祖先。

2. **最近公共祖先的定义**：
    - 如果一个节点的左子树和右子树分别包含 `p` 和 `q`，那么这个节点就是 `p` 和 `q` 的最近公共祖先。
    - 如果 `p` 和 `q` 都在某个子树中，那么该子树的根节点就是最近公共祖先。
    - 如果 `p` 或 `q` 等于当前节点，则返回该节点。

3. **递归搜索**：
    - 从根节点开始递归搜索左子树和右子树。
    - 如果左子树和右子树分别返回了 `p` 或 `q`，则当前节点就是最近公共祖先。
    - 如果某个子树返回了一个节点，表示在该子树中找到了 `p` 或 `q`，否则返回 `None`。

---

### **代码实现：**

```python
class TreeNode(object):
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

class Solution(object):
    def lowestCommonAncestor(self, root, p, q):
        """
        :type root: TreeNode
        :type p: TreeNode
        :type q: TreeNode
        :rtype: TreeNode
        """
        # 如果当前节点为空，或者当前节点就是p或q，则返回当前节点
        if not root or root == p or root == q:
            return root
        
        # 递归查找左右子树
        left = self.lowestCommonAncestor(root.left, p, q)
        right = self.lowestCommonAncestor(root.right, p, q)
        
        # 如果左右子树都返回非空，则说明p和q分别在当前节点的左右子树
        if left and right:
            return root
        
        # 否则返回非空的那个子树节点
        return left if left else right
```

---

### **解法解析：**

1. **递归函数定义**：
    - `lowestCommonAncestor(root, p, q)`：这是我们递归的主要函数。它的作用是：
        - 如果当前节点为空，或者当前节点就是 `p` 或 `q`，返回当前节点。
        - 否则递归查找左右子树的最近公共祖先。

2. **递归基准条件**：
    - 如果 `root` 为 `None`，直接返回 `None`。
    - 如果 `root` 等于 `p` 或 `q`，直接返回当前节点，因为当前节点已经是其中一个节点或目标之一。

3. **递归过程**：
    - 调用递归函数分别检查左子树和右子树，得到 `left` 和 `right` 的结果。
    - 如果 `left` 和 `right` 都不为空，表示 `p` 和 `q` 分别在左右子树中，当前节点就是它们的最近公共祖先。
    - 如果只有一个子树非空，说明 `p` 和 `q` 都在同一子树中，那么直接返回非空的子树结果。

4. **最终返回**：
    - 如果 `left` 和 `right` 都不为空，返回 `root`（即最近公共祖先）。
    - 如果只有一个子树非空，返回非空子树的结果。

---

### **时间复杂度与空间复杂度：**

1. **时间复杂度**：
    - 每个节点最多被访问一次，因此时间复杂度为 \(O(n)\)，其中 \(n\) 是树中节点的数量。

2. **空间复杂度**：
    - 由于递归的调用栈深度最大为树的高度，最坏情况下（树为链表结构）空间复杂度为 \(O(n)\)，最好情况下为 \(O(\log n)\)（平衡树）。

---

### **示例：**

假设给定的二叉树如下：

```
       3
      / \
     5   1
    / \ / \
   6  2 0  8
     / \
    7   4
```

- `p = 5`, `q = 1`
- 输出：`3`，因为 `3` 是 `5` 和 `1` 的最近公共祖先。

- `p = 5`, `q = 4`
- 输出：`5`，因为 `5` 是 `5` 和 `4` 的最近公共祖先。

---

### **总结：**
- 通过递归遍历树，我们可以找到任意两个节点的最近公共祖先。
- 基本的思路是利用递归深入左右子树，当左右子树分别包含 `p` 和 `q` 时，当前节点即为最近公共祖先。
- 时间复杂度为 \(O(n)\)，空间复杂度为 \(O(h)\)，其中 \(h\) 是树的高度。

这种方法简洁且高效，能够正确地找到任意两个节点的最近公共祖先。