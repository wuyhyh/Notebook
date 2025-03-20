from typing import List


class Solution:
    def max_square(self, matrix: List[List[int]]) -> int:
        if not matrix or not matrix[0]:
            return 0

        rows, cols = len(matrix), len(matrix[0])
        dp = [[0] * cols for _ in range(rows)]  # 初始化动态规划数组，其中的d[i][j]表示以i，j为右下角的正方形的边长
        max_side = 0  # 记录最大正方形的边长

        for i in range(rows):
            for j in range(cols):
                if matrix[i][j] == '1':
                    if i == 0 or j == 0:  # 第一行或者第一列
                        dp[i][j] = 1
                    else:
                        dp[i][j] = min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1]) + 1
                max_side = max(max_side, dp[i][j])  # 记录最大边长

        return max_side * max_side


if __name__ == "__main__":
    sol = Solution()
    matrix = [
        ["1", "0", "1", "0", "0"],
        ["1", "0", "1", "1", "1"],
        ["1", "1", "1", "1", "1"],
        ["1", "0", "0", "1", "0"]
    ]

    print(sol.max_square(matrix))
