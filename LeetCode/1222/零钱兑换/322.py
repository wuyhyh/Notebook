def coinChange(coins, amount):
    # 初始化 dp 数组，dp[i] 表示金额 i 的最少硬币数
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0  # 0 元不需要任何硬币

    # 遍历每个硬币
    for coin in coins:
        # 更新每个金额的最小硬币数
        for i in range(coin, amount + 1):
            dp[i] = min(dp[i], dp[i - coin] + 1)

    # 如果 dp[amount] 仍为 inf，说明无法组成该金额
    return dp[amount] if dp[amount] != float('inf') else -1
