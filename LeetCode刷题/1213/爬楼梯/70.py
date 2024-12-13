class Solution:
    def climbStairs(self, n: int) -> int:
        # 边界条件
        if n == 1:
            return 1

        # 初始化 dp 数组
        dp = [0] * (n + 1)
        dp[0] = 1  # 到达第0阶楼梯的方法数是1（不爬楼梯）
        dp[1] = 1  # 到达第1阶楼梯的方法数是1（爬一步）

        # 填充 dp 数组
        for i in range(2, n + 1):
            dp[i] = dp[i - 1] + dp[i - 2]

        # 返回 dp[n]，即到达第 n 阶楼梯的方法数
        return dp[n]
