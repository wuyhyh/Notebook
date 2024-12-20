def generateParenthesis(n):
    result = []

    def backtrack(current_string, open_count, close_count):
        # 如果当前字符串的长度达到 2 * n，说明是一个有效组合
        if len(current_string) == 2 * n:
            result.append(current_string)
            return

        # 如果左括号的数量小于 n，可以添加一个左括号
        if open_count < n:
            backtrack(current_string + '(', open_count + 1, close_count)

        # 如果右括号的数量小于左括号的数量，可以添加一个右括号
        if close_count < open_count:
            backtrack(current_string + ')', open_count, close_count + 1)

    # 初始化回溯，当前字符串为空，左括号和右括号数量都为 0
    backtrack("", 0, 0)

    return result
