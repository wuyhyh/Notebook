from typing import List


class Solution:
    def partition(self, s: str) -> List[List[str]]:
        result = []

        # 判断是否是回文串
        def is_palindrome(s):
            return s == s[::-1]

        # 回溯函数，start表示要切割的开始位置，path表示一个切割方案
        def backtrack(start: int, path: List[str]):
            if start == len(s):  # 到达了字符串末尾，保存当前路径
                result.append(path[:])
                return

            # 从start开始，尝试切割每一个可能的字符串
            for end in range(start, len(s)):
                substring = s[start:end + 1]
                if is_palindrome(substring):  # 如果是回文，继续递归
                    path.append(substring)
                    backtrack(end + 1, path)
                    path.pop()  # 撤销选择

        backtrack(0, [])
        return result


if __name__ == "__main__":
    sol = Solution()
    print(sol.partition("aab"))
