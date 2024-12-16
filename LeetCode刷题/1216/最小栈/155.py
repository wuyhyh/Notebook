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
