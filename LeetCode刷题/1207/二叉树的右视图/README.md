LeetCode 第199题：“二叉树的右视图”（**Binary Tree Right Side View**）要求返回从二叉树的右侧看到的节点值。右视图是从右侧观察二叉树时，每一层的最右边节点。

---

### 思路：
1. **层序遍历（广度优先搜索，BFS）**：
    - 使用队列进行层序遍历。
    - 每次遍历到某一层的最后一个节点时，将其值添加到结果列表中。
    - 逐层处理，最终返回右视图的节点值列表。

2. **深度优先搜索（DFS）**：
    - 使用递归的方式，从根节点开始优先遍历右子树，然后左子树。
    - 记录每层第一个访问的节点值，将其添加到结果列表中。

---

### 方法一：层序遍历（BFS）

#### 代码实现：

```python
from collections import deque

class Solution(object):
    def rightSideView(self, root):
        """
        :type root: TreeNode
        :rtype: List[int]
        """
        if not root:
            return []
        
        result = []
        queue = deque([root])  # 使用队列进行层序遍历
        
        while queue:
            level_size = len(queue)
            for i in range(level_size):
                node = queue.popleft()
                
                # 如果是当前层的最后一个节点，加入结果
                if i == level_size - 1:
                    result.append(node.val)
                
                # 将左右子节点加入队列
                if node.left:
                    queue.append(node.left)
                if node.right:
                    queue.append(node.right)
        
        return result
```

#### 解释：
1. **队列实现层序遍历**：
    - 使用 `deque` 队列存储当前层的节点。
    - 每次从队列中取出一个节点，检查它是否是当前层的最后一个节点。如果是，将它的值加入结果列表。
2. **层序控制**：
    - 通过记录当前层的节点数量（`level_size`），区分不同层。
3. **时间复杂度和空间复杂度**：
    - **时间复杂度**：\(O(n)\)，每个节点访问一次。
    - **空间复杂度**：\(O(n)\)，队列中最多存储一层的节点。

---

### 方法二：深度优先搜索（DFS）

#### 代码实现：

```python
class Solution(object):
    def rightSideView(self, root):
        """
        :type root: TreeNode
        :rtype: List[int]
        """
        result = []
        
        def dfs(node, depth):
            if not node:
                return
            
            # 如果当前深度没有记录节点，添加到结果
            if depth == len(result):
                result.append(node.val)
            
            # 优先遍历右子树，再遍历左子树
            dfs(node.right, depth + 1)
            dfs(node.left, depth + 1)
        
        dfs(root, 0)
        return result
```

#### 解释：
1. **深度优先搜索**：
    - 递归优先遍历右子树，然后左子树，确保右侧节点优先被记录。
    - 使用深度（`depth`）作为当前层的标识，只有第一次访问该深度时才记录节点值。
2. **递归终止条件**：
    - 当节点为空时，停止递归。
3. **时间复杂度和空间复杂度**：
    - **时间复杂度**：\(O(n)\)，每个节点访问一次。
    - **空间复杂度**：\(O(h)\)，递归栈的深度等于树的高度。

---

### 示例：

给定二叉树：
```
       1
      / \
     2   3
      \    \
       5    4
```

输出：`[1, 3, 4]`

#### 层序遍历（BFS）过程：
1. **第一层**：`[1]`，最右节点是 `1`。
2. **第二层**：`[2, 3]`，最右节点是 `3`。
3. **第三层**：`[5, 4]`，最右节点是 `4`。

#### 深度优先搜索（DFS）过程：
1. 从根节点 `1` 开始，记录深度 `0` 的第一个节点值为 `1`。
2. 递归遍历右子树，记录深度 `1` 的第一个节点值为 `3`。
3. 继续递归右子树，记录深度 `2` 的第一个节点值为 `4`。

最终结果：`[1, 3, 4]`

---

### 总结：
- **BFS（层序遍历）**：更直观，逐层处理，适合熟悉广度优先遍历的人。
- **DFS（深度优先搜索）**：优先右子树，代码较简洁，但需要递归栈。

两种方法都可以高效解决问题，选择适合自己的实现方式即可！
