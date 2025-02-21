class Solution:
    def uniquePaths(self, m: int, n: int) -> int:
        # 创建一个 m x n 的二维 DP 数组
        dp = [[1] * n for _ in range(m)]

        # 填充 DP 数组，注意边界条件已经设置为 1
        for i in range(1, m):
            for j in range(1, n):
                dp[i][j] = dp[i-1][j] + dp[i][j-1]

        # 返回右下角的路径数
        return dp[m-1][n-1]
