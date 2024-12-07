LeetCode 第230题：“二叉搜索树中第K小的元素”（**Kth Smallest Element in a BST**）要求我们在二叉搜索树（BST）中找到第 \(k\) 小的元素。

---

### 思路：
由于二叉搜索树的中序遍历（左 -> 根 -> 右）会生成一个有序的节点值列表，我们只需对树进行中序遍历，当遍历到第 \(k\) 个节点时，直接返回其值。

1. **中序遍历法（递归）**：
    - 使用递归对树进行中序遍历。
    - 通过一个计数器来记录当前遍历到的节点序号，当计数器等于 \(k\) 时返回当前节点的值。

2. **中序遍历法（迭代）**：
    - 使用栈模拟递归，实现中序遍历。
    - 逐步访问节点的左子树 -> 当前节点 -> 右子树，当计数器等于 \(k\) 时，返回当前节点的值。

---

### 方法一：递归法

#### 代码实现：

```python
class Solution(object):
    def kthSmallest(self, root, k):
        """
        :type root: TreeNode
        :type k: int
        :rtype: int
        """
        self.count = 0  # 当前访问的节点计数
        self.result = None  # 第 k 小的节点值

        def inorder(node):
            if not node or self.result is not None:
                return
            
            # 递归遍历左子树
            inorder(node.left)
            
            # 访问当前节点
            self.count += 1
            if self.count == k:
                self.result = node.val
                return
            
            # 递归遍历右子树
            inorder(node.right)
        
        inorder(root)
        return self.result
```

#### 解释：
1. **计数器**：`self.count` 用于记录当前中序遍历的节点序号。
2. **终止条件**：
    - 如果节点为空（`None`），直接返回。
    - 如果已经找到了结果（`self.result` 不为空），停止进一步的递归。
3. **递归过程**：
    - 按中序遍历的顺序（左 -> 根 -> 右）递归访问节点。
    - 每访问一个节点，计数器加 1。当计数器等于 \(k\) 时，记录当前节点值并停止递归。

---

### 方法二：迭代法

#### 代码实现：

```python
class Solution(object):
    def kthSmallest(self, root, k):
        """
        :type root: TreeNode
        :type k: int
        :rtype: int
        """
        stack = []
        count = 0
        
        while stack or root:
            # 逐步遍历左子树
            while root:
                stack.append(root)
                root = root.left
            
            # 访问当前节点
            root = stack.pop()
            count += 1
            if count == k:
                return root.val
            
            # 转向右子树
            root = root.right
```

#### 解释：
1. **栈模拟中序遍历**：
    - 使用栈将当前节点及其左子树依次压入栈。
    - 弹出栈顶节点并访问当前节点。
2. **计数器**：
    - 每访问一个节点，计数器加 1。当计数器等于 \(k\) 时，返回当前节点值。
3. **右子树**：
    - 访问完当前节点后，转向右子树，继续上述过程。

---

### 示例：

给定二叉搜索树：
```
       3
      / \
     1   4
      \
       2
```

- \(k = 1\)：中序遍历顺序为 `[1, 2, 3, 4]`，第 1 小的元素是 `1`。
- \(k = 2\)：中序遍历顺序为 `[1, 2, 3, 4]`，第 2 小的元素是 `2`。

---

### 时间复杂度与空间复杂度：
1. **时间复杂度**：\(O(h + k)\)
    - \(h\) 是树的高度。
    - 中序遍历需要 \(O(h)\) 时间到达最左节点，之后再遍历 \(k\) 个节点。
2. **空间复杂度**：
    - 递归法：\(O(h)\)，递归栈的深度为树的高度。
    - 迭代法：\(O(h)\)，栈的最大深度为树的高度。

---

### 总结：
- **递归法**：代码简洁，容易理解，适合树较小或递归栈深度可控的场景。
- **迭代法**：避免递归栈，适合树较大的情况，通常更通用。

两种方法都可以有效解决问题，选择适合自己的方式即可！
