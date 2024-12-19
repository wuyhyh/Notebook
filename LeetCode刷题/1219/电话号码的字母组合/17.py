def letterCombinations(digits):
    if not digits:
        return []

    # 映射每个数字到相应的字母
    digit_to_char = {
        "2": "abc", "3": "def", "4": "ghi", "5": "jkl",
        "6": "mno", "7": "pqrs", "8": "tuv", "9": "wxyz"
    }

    result = []

    def backtrack(index, current_combination):
        # 如果当前字母组合的长度与输入的数字字符串长度一致，加入结果
        if index == len(digits):
            result.append(current_combination)
            return

        # 获取当前数字对应的字母集
        current_digit = digits[index]
        for char in digit_to_char[current_digit]:
            backtrack(index + 1, current_combination + char)

    # 从第一个数字开始回溯
    backtrack(0, "")

    return result
