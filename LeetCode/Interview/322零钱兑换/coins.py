from typing import List


class Solution:
    def coin_change(self, coins: List[int], amount: int) -> int:
        dp = [amount + 1] * (amount + 1)  # dp[i]代表凑成金额i所需要的最少的硬币个数，初始化化为amount+1，这是一个范围外的值
        dp[0] = 0

        for coin in coins:  # 尝试不同面值的硬币
            for i in range(coin, amount + 1):
                dp[i] = min(dp[i], dp[i - coin] + 1)  # 最优解

        return dp[amount] if dp[amount] != (amount + 1) else -1  # 如果dp[amount]的值还是初值，说明不存在解决方案


if __name__ == '__main__':
    coins = [1, 2, 5]
    amount = 3
    solution = Solution()
    print(solution.coin_change(coins, amount))
