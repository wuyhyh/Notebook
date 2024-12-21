import math

def numSquares(n):
    # 初始化dp数组，dp[i]表示i的最少完全平方数的个数
    dp = [float('inf')] * (n + 1)
    dp[0] = 0  # 0 需要 0 个完全平方数

    # 填充dp数组
    for i in range(1, n + 1):
        j = 1
        while j * j <= i:
            dp[i] = min(dp[i], dp[i - j * j] + 1)
            j += 1

    return dp[n]
