下面是针对 **LeetCode 第437题：路径总和 III** 的完整解法和文档整理。

---

## **LeetCode 第437题：路径总和 III（Path Sum III）**

### **题目描述：**
给定一个二叉树的根节点 `root` 和一个目标和 `sum`，找出二叉树中路径和等于给定值的路径的个数。路径的定义是从某个节点到任意节点的路径，并且路径方向是沿着父子节点的。

### **问题分析：**
1. **路径的定义**：
    - 从树中的任意节点出发，沿着树的父子关系进行前进。
    - 路径的和是路径上所有节点值的累加。

2. **解题关键**：
    - **前缀和**的技巧：通过记录当前节点到根节点路径的累积和，可以快速找到路径和为目标值的路径。
    - **递归遍历**：每次从当前节点出发，计算路径和，并查找该路径是否满足目标值。
    - **哈希表**：通过哈希表记录已访问过的路径和，避免重复计算路径和。

---

### **解法一：递归 + 哈希表**

我们可以用哈希表记录从根节点到当前节点的路径和。递归遍历二叉树时，更新路径和并检查从某个节点到当前节点的路径和是否等于目标值 `sum`。

#### **代码实现：**

```python
class TreeNode(object):
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

class Solution(object):
    def pathSum(self, root, sum):
        """
        :type root: TreeNode
        :type sum: int
        :rtype: int
        """
        # 记录当前路径和出现的次数
        path_count = {0: 1}  # 初始化，表示从根节点开始的路径和为0的路径有1条
        return self.dfs(root, sum, 0, path_count)
    
    def dfs(self, node, target, current_sum, path_count):
        if not node:
            return 0
        
        # 更新当前路径的和
        current_sum += node.val
        
        # 计算当前路径中有多少个子路径的和为target
        result = path_count.get(current_sum - target, 0)
        
        # 更新哈希表：增加当前路径和出现的次数
        path_count[current_sum] = path_count.get(current_sum, 0) + 1
        
        # 递归遍历左右子树
        result += self.dfs(node.left, target, current_sum, path_count)
        result += self.dfs(node.right, target, current_sum, path_count)
        
        # 回溯，移除当前节点的路径和
        path_count[current_sum] -= 1
        
        return result
```

---

### **解法解析：**
1. **递归遍历二叉树**：
    - 使用递归深度优先遍历（DFS），从树的每一个节点出发，检查以当前节点为起点的路径和是否为目标值。

2. **前缀和与哈希表**：
    - `current_sum` 记录从当前节点到根节点的路径和。
    - `path_count` 哈希表记录了从根节点到每个节点的路径和出现的次数。
    - 如果 `current_sum - target` 存在于 `path_count` 中，说明从某个节点到当前节点的路径和为目标值。

3. **回溯**：
    - 在递归过程中，需要回溯时减去当前节点的路径和，以保持哈希表的正确性。

---

### **时间复杂度与空间复杂度：**
- **时间复杂度**：\(O(n)\)，其中 \(n\) 是树的节点数量。每个节点被遍历一次，每次访问节点时进行常数时间的操作。
- **空间复杂度**：\(O(n)\)，主要由递归栈和哈希表 `path_count` 占用的空间决定。在最坏情况下，哈希表需要存储树的每个节点的路径和。

---

### **示例：**

假设给定的二叉树是：

```
       10
      /  \
     5   -3
    / \    \
   3   2    11
  / \   \
 3   -2   1
```

目标路径和 `sum = 8`，输出应该为 `3`，因为有三条路径的和为 `8`，分别是：
- `5 -> 3`（路径和为 8）
- `5 -> 2 -> 1`（路径和为 8）
- `-3 -> 11`（路径和为 8）

---

### **调试与常见问题：**
1. **`TypeError` 问题**：若出现 `TypeError: unsupported operand type(s) for -: 'int' and 'builtin_function_or_method'` 错误，通常是因为 `target` 或 `current_sum` 被误赋值为函数或方法。确保这两个变量在递归中始终是整数类型。

   例如，检查传递给 `pathSum()` 函数的 `sum` 参数，确保它是一个整数。

2. **递归终止条件**：如果树是空树，递归函数应及时返回 `0`，以避免进一步的错误。

---

### **总结：**
- 通过递归遍历二叉树，结合哈希表记录路径和，能够有效找到路径和为目标值的路径数量。
- 利用**前缀和**技巧，通过哈希表存储路径和的频次，使得问题能够高效地解决。
