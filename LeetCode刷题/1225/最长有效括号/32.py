def longestValidParentheses(s: str) -> int:
    stack = [-1]  # 栈初始化，加入 -1 帮助计算有效括号子串长度
    max_len = 0

    for i, char in enumerate(s):
        if char == '(':
            stack.append(i)  # 左括号入栈
        else:
            stack.pop()  # 右括号出栈
            if not stack:
                stack.append(i)  # 如果栈为空，表示当前右括号无法匹配，加入其索引
            else:
                max_len = max(max_len, i - stack[-1])  # 计算有效括号长度

    return max_len
