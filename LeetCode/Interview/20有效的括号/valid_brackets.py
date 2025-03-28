class Solution:
    def isValid(self, s: str) -> bool:
        bracket_map = {
            ')': '(',
            ']': '[',
            '}': '{',
        }

        stack = []

        for char in s:
            if char in bracket_map:
                # 如果字符是右括号，检查栈顶是否匹配
                top_element = stack.pop() if stack else '#'
                if bracket_map[char] != top_element:
                    return False
            else:
                # 左括号，压入栈中
                stack.append(char)

        # 栈为空，说明匹配成功
        return not stack


if __name__ == '__main__':
    solution = Solution()
    s = "({[([)])]})"
    print(solution.isValid(s))
