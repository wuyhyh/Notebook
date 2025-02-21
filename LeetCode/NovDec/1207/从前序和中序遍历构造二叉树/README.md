LeetCode 第105题：“从前序与中序遍历序列构造二叉树”（**Construct Binary Tree from Preorder and Inorder Traversal**）要求我们根据给定的二叉树的前序遍历和中序遍历结果，构造出该二叉树。

---

### 思路：
1. **前序遍历**的性质：
    - 前序遍历的第一个元素是当前树的根节点。
2. **中序遍历**的性质：
    - 中序遍历中，根节点将树分为两部分：
        - 左子树的所有节点在根节点的左边。
        - 右子树的所有节点在根节点的右边。
3. 结合前序和中序遍历，我们可以递归地构造树：
    - 从前序遍历中确定根节点；
    - 在中序遍历中找到根节点的位置，从而划分出左子树和右子树；
    - 递归构造左子树和右子树。

---

### 递归实现：

#### 代码实现：

```python
class TreeNode(object):
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

class Solution(object):
    def buildTree(self, preorder, inorder):
        """
        :type preorder: List[int]
        :type inorder: List[int]
        :rtype: TreeNode
        """
        if not preorder or not inorder:
            return None
        
        # 前序遍历的第一个元素是当前树的根节点
        root_val = preorder[0]
        root = TreeNode(root_val)
        
        # 在中序遍历中找到根节点的位置
        root_index = inorder.index(root_val)
        
        # 左子树的节点数量为中序遍历中根节点左边的节点数量
        left_size = root_index
        
        # 构造左子树和右子树
        root.left = self.buildTree(preorder[1:1+left_size], inorder[:root_index])
        root.right = self.buildTree(preorder[1+left_size:], inorder[root_index+1:])
        
        return root
```

---

### 解析：
1. **根节点的确定**：
    - 从前序遍历的第一个元素中确定当前树的根节点。
    - 在中序遍历中查找根节点的位置，分割出左子树和右子树。
2. **递归划分子树**：
    - 使用分割出的左子树和右子树对应的前序和中序遍历序列，递归构造左子树和右子树。
3. **递归终止条件**：
    - 当前序或中序遍历为空时，返回 `None`。

---

### 示例：

输入：
```python
preorder = [3, 9, 20, 15, 7]
inorder = [9, 3, 15, 20, 7]
```

输出的二叉树为：
```
       3
      / \
     9  20
       /  \
      15   7
```

**构造过程**：
1. 根节点为 `3`（前序遍历第一个元素）。
2. 在中序遍历中，`3` 的位置将数组分为 `[9]` 和 `[15, 20, 7]`：
    - 左子树的中序遍历为 `[9]`，对应的前序遍历为 `[9]`。
    - 右子树的中序遍历为 `[15, 20, 7]`，对应的前序遍历为 `[20, 15, 7]`。
3. 递归构造左子树和右子树。

---

### 时间复杂度和空间复杂度：
1. **时间复杂度**：
    - 查找根节点在中序遍历中的位置需要 \(O(n)\)，总的时间复杂度为 \(O(n^2)\)。
    - 如果使用哈希表预处理中序遍历以快速查找位置，时间复杂度可以优化为 \(O(n)\)。
2. **空间复杂度**：
    - 递归栈的深度为二叉树的高度，最坏情况下（退化为链表）为 \(O(n)\)，平均情况下为 \(O(\log n)\)。

---

### 优化（使用哈希表）：

为了优化查找根节点在中序遍历中的位置，可以使用哈希表预处理：

```python
class Solution(object):
    def buildTree(self, preorder, inorder):
        """
        :type preorder: List[int]
        :type inorder: List[int]
        :rtype: TreeNode
        """
        # 构建中序遍历值到索引的映射
        inorder_index_map = {val: idx for idx, val in enumerate(inorder)}
        
        def helper(preorder_start, preorder_end, inorder_start, inorder_end):
            if preorder_start > preorder_end:
                return None
            
            # 根节点是前序遍历的第一个元素
            root_val = preorder[preorder_start]
            root = TreeNode(root_val)
            
            # 找到根节点在中序遍历中的位置
            root_index = inorder_index_map[root_val]
            
            # 左子树的节点数量
            left_size = root_index - inorder_start
            
            # 构造左子树和右子树
            root.left = helper(preorder_start + 1, preorder_start + left_size, inorder_start, root_index - 1)
            root.right = helper(preorder_start + left_size + 1, preorder_end, root_index + 1, inorder_end)
            
            return root
        
        return helper(0, len(preorder) - 1, 0, len(inorder) - 1)
```

---

### 总结：
- **递归构造树**：通过前序和中序遍历的性质递归构造二叉树。
- **时间优化**：使用哈希表加速根节点查找，避免 \(O(n^2)\) 时间复杂度。
- **两种实现**：可选择直接分割列表或基于索引范围进行构造，后一种方法更高效。
