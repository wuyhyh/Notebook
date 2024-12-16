def decodeString(s: str) -> str:
    stack = []  # 用来存储当前解码的状态（重复次数和解码字符串）
    current_string = ""  # 当前构建的字符串
    current_num = 0  # 当前的重复次数

    for char in s:
        if char.isdigit():
            # 构造重复次数，可能有多位数字
            current_num = current_num * 10 + int(char)
        elif char == '[':
            # 遇到左括号时，将当前重复次数和构建的字符串入栈
            stack.append((current_num, current_string))
            current_num = 0  # 重置重复次数
            current_string = ""  # 重置当前字符串
        elif char == ']':
            # 遇到右括号时，弹出栈顶元素并解码
            last_num, last_string = stack.pop()
            current_string = last_string + current_string * last_num
        else:
            # 遇到字母时，添加到当前构建的字符串
            current_string += char

    return current_string
