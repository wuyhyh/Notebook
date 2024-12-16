### **LeetCode 第155题 - 最小栈 (Min Stack)**

#### **题目描述**

设计一个支持 **push**, **pop**, **top**, 和 **retrieving the minimum element** 操作的栈。

实现 `MinStack` 类：

- **`push(val: int)`** - 将元素 `val` 推入栈中。
- **`pop()`** - 移除栈顶元素。
- **`top()`** - 获取栈顶元素。
- **`getMin()`** - 获取栈中的最小元素。

#### **要求**

- 你必须在 **常数时间** 内完成 `getMin` 操作。

### **解题思路**

1. **普通栈的实现**：
    - 一般的栈只需要一个列表（或者用 Python 的 `list` 类型）来模拟即可。

2. **优化 `getMin`**：
    - 为了保证 `getMin()` 操作能在 **常数时间** 内完成，我们需要引入一个额外的数据结构，用来存储栈中当前的最小值。
    - 在 `push` 操作时，我们不仅将元素压入栈，还需要记录当前栈中的最小值。
    - 在 `pop` 操作时，我们也同时移除当前栈中的最小值。

3. **如何实现**：
    - 使用两个栈：
        - **主栈**：用于存储所有的元素。
        - **最小栈**：用于存储当前栈中的最小值。每次 `push` 操作时，将当前最小值压入最小栈；每次 `pop` 时，最小栈也同步弹出。

### **代码实现**

```python
class MinStack:

    def __init__(self):
        # 主栈，用来存储所有的元素
        self.stack = []
        # 最小栈，用来存储当前栈中的最小值
        self.min_stack = []

    def push(self, val: int) -> None:
        # 将元素压入主栈
        self.stack.append(val)
        # 将当前的最小值压入最小栈
        if not self.min_stack or val <= self.min_stack[-1]:
            self.min_stack.append(val)

    def pop(self) -> None:
        # 弹出栈顶元素
        if self.stack:
            popped = self.stack.pop()
            # 如果弹出的元素是最小栈的栈顶元素，则最小栈也弹出该元素
            if popped == self.min_stack[-1]:
                self.min_stack.pop()

    def top(self) -> int:
        # 返回栈顶元素
        return self.stack[-1] if self.stack else None

    def getMin(self) -> int:
        # 返回最小栈的栈顶元素，即当前栈中的最小值
        return self.min_stack[-1] if self.min_stack else None
```

### **代码解析**

1. **`__init__` 方法**：
    - 初始化两个栈：`stack`（主栈）和 `min_stack`（最小栈）。

2. **`push(val)` 方法**：
    - 将元素 `val` 压入主栈 `stack` 中。
    - 如果 `min_stack` 为空或者 `val` 小于等于 `min_stack` 的栈顶元素，说明当前元素 `val` 是新的最小值，我们将其压入最小栈。

3. **`pop()` 方法**：
    - 弹出主栈的栈顶元素。
    - 如果弹出的元素是最小栈的栈顶元素，说明栈中的最小值发生了变化，我们也需要从最小栈中弹出相应的元素。

4. **`top()` 方法**：
    - 返回主栈的栈顶元素。

5. **`getMin()` 方法**：
    - 返回最小栈的栈顶元素，即当前栈中的最小值。

### **时间复杂度**

- **`push(val)`**：`O(1)`，每次 `push` 操作只需要将元素压入主栈和最小栈，都是常数时间操作。
- **`pop()`**：`O(1)`，每次 `pop` 操作只需要弹出栈顶元素，并在必要时弹出最小栈中的元素。
- **`top()`**：`O(1)`，直接访问栈顶元素。
- **`getMin()`**：`O(1)`，直接访问最小栈的栈顶元素。

### **空间复杂度**

- **空间复杂度**：`O(n)`，其中 `n` 是栈中元素的数量。我们使用了两个栈，主栈和最小栈，最坏情况下，两个栈的大小都为 `n`。

### **示例**

#### 示例 1：

```python
min_stack = MinStack()
min_stack.push(-2)
min_stack.push(0)
min_stack.push(-3)

print(min_stack.getMin())  # 输出 -3
min_stack.pop()
print(min_stack.top())     # 输出 0
print(min_stack.getMin())  # 输出 -2
```

**解释**：
- `push(-2)` 后，`stack` = `[-2]`, `min_stack` = `[-2]`。
- `push(0)` 后，`stack` = `[-2, 0]`, `min_stack` = `[-2]`。
- `push(-3)` 后，`stack` = `[-2, 0, -3]`, `min_stack` = `[-2, -3]`。
- `getMin()` 返回最小值 `-3`。
- `pop()` 后，`stack` = `[-2, 0]`, `min_stack` = `[-2]`。
- `top()` 返回 `0`。
- `getMin()` 返回最小值 `-2`。

### **总结**

- 通过使用两个栈，一个保存所有元素，另一个保存当前最小值，我们可以在常数时间内实现获取栈中最小值的操作。
- `push`, `pop`, `top`, `getMin` 都能在 `O(1)` 时间复杂度内完成。
