def isValid(s: str) -> bool:
    # 定义一个栈来保存左括号
    stack = []

    # 定义一个字典，映射右括号到对应的左括号
    bracket_map = {')': '(', '}': '{', ']': '['}

    # 遍历字符串中的每个字符
    for char in s:
        if char in bracket_map:
            # 如果是右括号，弹出栈顶的左括号
            top_element = stack.pop() if stack else '#'

            # 如果左括号与右括号不匹配，返回 False
            if bracket_map[char] != top_element:
                return False
        else:
            # 如果是左括号，压入栈中
            stack.append(char)

    # 最后，如果栈为空，说明括号匹配正确
    return not stack
