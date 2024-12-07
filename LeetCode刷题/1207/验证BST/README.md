LeetCode 第98题：“验证二叉搜索树”（**Validate Binary Search Tree**）要求判断一棵二叉树是否是一个有效的二叉搜索树（BST）。一个二叉搜索树具有以下性质：
1. 左子树所有节点的值都小于当前节点的值。
2. 右子树所有节点的值都大于当前节点的值。
3. 左右子树也必须是二叉搜索树。

---

### 思路：
有两种常见解法：
1. **递归验证范围法**：
    - 对于每个节点，维护一个合法值范围 `[min_val, max_val]`。
    - 检查当前节点值是否在范围内。
    - 对左子树递归更新范围为 `[min_val, root.val)`；
      对右子树递归更新范围为 `(root.val, max_val]`。

2. **中序遍历法**：
    - 中序遍历二叉搜索树时，节点值应该是严格递增的。
    - 使用一个变量记录前一个访问的节点值，确保当前节点值大于前一个值。

---

### 方法一：递归验证范围法

#### 代码实现：

```python
class Solution(object):
    def isValidBST(self, root):
        """
        :type root: TreeNode
        :rtype: bool
        """
        def validate(node, min_val, max_val):
            # 空节点默认是合法的
            if not node:
                return True
            
            # 当前节点值必须在 (min_val, max_val) 范围内
            if not (min_val < node.val < max_val):
                return False
            
            # 递归验证左右子树
            return (validate(node.left, min_val, node.val) and
                    validate(node.right, node.val, max_val))
        
        # 初始范围是 (-∞, +∞)
        return validate(root, float('-inf'), float('inf'))
```

#### 解释：
1. **`validate` 函数**：
    - 检查当前节点值是否在合法范围内 `[min_val, max_val]`。
    - 递归调用左右子树时更新范围：左子树范围为 `[min_val, root.val)`，右子树范围为 `(root.val, max_val]`。
2. **递归终止条件**：
    - 如果节点为空，返回 `True`，表示合法。
    - 如果节点值不在合法范围内，返回 `False`。
3. 初始范围为整个数轴 \((-∞, +∞)\)。

---

### 方法二：中序遍历法

#### 代码实现：

```python
class Solution(object):
    def isValidBST(self, root):
        """
        :type root: TreeNode
        :rtype: bool
        """
        stack = []
        prev_val = float('-inf')  # 记录中序遍历的前一个节点值
        
        while stack or root:
            # 遍历左子树
            while root:
                stack.append(root)
                root = root.left
            
            # 访问当前节点
            root = stack.pop()
            # 中序遍历中，当前节点值必须大于前一个节点值
            if root.val <= prev_val:
                return False
            prev_val = root.val
            
            # 遍历右子树
            root = root.right
        
        return True
```

#### 解释：
1. **中序遍历**：
    - 使用栈模拟递归，通过栈实现对二叉树的中序遍历。
2. **合法性检查**：
    - 在中序遍历过程中，当前节点值必须大于前一个节点值。如果不满足，直接返回 `False`。
3. **初始值**：
    - `prev_val` 初始值设置为负无穷，用于与第一个节点比较。

---

### 示例：

给定二叉树：
```
    2
   / \
  1   3
```

#### 方法一（递归验证范围）：
1. 初始范围是 \((-∞, +∞)\)。
2. 对根节点 `2`：
    - 检查是否在 \((-∞, +∞)\) 范围内（合法）。
    - 左子树范围更新为 \((-∞, 2)\)，右子树范围更新为 \((2, +∞)\)。
3. 对左子节点 `1`：
    - 检查是否在 \((-∞, 2)\) 范围内（合法）。
    - 子节点为空，返回 `True`。
4. 对右子节点 `3`：
    - 检查是否在 \((2, +∞)\) 范围内（合法）。
    - 子节点为空，返回 `True`。
5. 返回 `True`。

---

### 时间复杂度与空间复杂度：
- **时间复杂度**：
    - 两种方法的时间复杂度都是 \(O(n)\)，其中 \(n\) 是树的节点数。每个节点访问一次。
- **空间复杂度**：
    - 方法一（递归验证范围法）：空间复杂度是 \(O(h)\)，其中 \(h\) 是树的高度（递归栈深度）。
    - 方法二（中序遍历法）：空间复杂度是 \(O(h)\)，因为栈的最大深度取决于树的高度。

---

### 总结：
- **递归验证范围法**：逻辑清晰，适合喜欢递归的场景。
- **中序遍历法**：通过迭代实现，避免递归栈溢出，适合大树的情况。

两种方法都可以有效验证二叉树是否为有效的二叉搜索树，根据个人习惯选择即可！
