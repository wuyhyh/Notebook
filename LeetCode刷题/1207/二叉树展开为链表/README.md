### LeetCode 114题：二叉树展张为链表

该题要求将一个二叉树展张为一个指向链表，并要求根据先序遍历的顺序展张。链表通过右指针连接，所有左指针都要设置为空。

---

### 思路解析

1. **先序遍历特性：**
   先遍历顺序为：左子树 -> 根节点 -> 右子树，所以在展张时，左子树会先于右子树被处理。

2. **三种解法：**
    - **递序解法（往后遍历）：** 先对右子树和左子树进行递序展张，然后连接子树。
    - **逆序解法：** 通过一个栈来模拟先序遍历，指定字节点进行链表连接。
    - **Morris 遍历：** 通过根节点直接进行不依赖额外空间的实施。

---

### 方法一：递序解法（往后遍历）

#### 代码实现

```python
class Solution(object):
    def flatten(self, root):
        """
        :type root: TreeNode
        :rtype: None Do not return anything, modify root in-place instead.
        """
        if not root:
            return
        
        # 对右子树和左子树进行递序展张
        self.flatten(root.right)
        self.flatten(root.left)
        
        # 展张当前节点
        temp = root.right
        root.right = root.left
        root.left = None
        
        # 将原右子树链接到当前右子树底部
        curr = root
        while curr.right:
            curr = curr.right
        curr.right = temp
```

#### 说明
- **递序遍历：** 先对右子树和左子树进行展张，然后将左子树移动到右子树位置，并将原右子树连接到新右子树底部。
- **程序处理顺序：** 左子树 -> 右子树 -> 当前节点。

---

### 方法二：栈模拟先序遍历（逆序）

#### 代码实现

```python
from collections import deque

class Solution(object):
    def flatten(self, root):
        """
        :type root: TreeNode
        :rtype: None Do not return anything, modify root in-place instead.
        """
        if not root:
            return
        
        stack = [root]
        prev = None
        
        while stack:
            curr = stack.pop()
            
            if prev:
                prev.right = curr
                prev.left = None
            
            if curr.right:
                stack.append(curr.right)
            if curr.left:
                stack.append(curr.left)
            
            prev = curr
```

#### 说明
- **使用栈：** 将字节点按先序应该出现的顺序层层压入。
- **每一次过程：** 将当前节点连接到前一个节点右侧，并确保左指针为 None。

---

### 方法三：Morris遍历（原地修改）

#### 代码实现

```python
class Solution(object):
    def flatten(self, root):
        """
        :type root: TreeNode
        :rtype: None Do not return anything, modify root in-place instead.
        """
        curr = root
        
        while curr:
            if curr.left:
                # 找到左子树最右节点
                rightmost = curr.left
                while rightmost.right:
                    rightmost = rightmost.right
                
                # 将原右子树链接到左子树最右节点之后
                rightmost.right = curr.right
                
                # 将左子树移动到右子树，并清空左指针
                curr.right = curr.left
                curr.left = None
            
            # 进入下一个节点
            curr = curr.right
```

#### 说明
- **使用 Morris 遍历：** 将左子树最右节点作为当前节点的右子树之前置，以完续连接。
- **无额外空间：** 原地修改不需要栈，这是最高效的解法。

---

### 总结
1. **时间处理：**
    - 所有方法都是\u $O(n)$ ，因为每个节点只访问一次。

2. **空间处理：**
    - 递序和栈解法需要 $O(h)$ 空间，其中 $h$ 是树高度。
    - Morris遍历需要 $O(1)$ 空间，是最优解。

3. **选择：**
    - 如果需要构造不依赖额外空间，优先考虑 Morris 遍历。
    - 如果质性求明，将字节点根据先序展张，可使用栈法实现。

    