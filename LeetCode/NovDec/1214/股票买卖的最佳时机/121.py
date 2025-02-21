class Solution:
    def maxProfit(self, prices: list[int]) -> int:
        # 初始化买入的最低价格为正无穷，最大利润为0
        min_price = float('inf')
        max_profit = 0

        for price in prices:
            # 更新最低买入价格
            if price < min_price:
                min_price = price
            # 计算当前卖出后的利润，并更新最大利润
            max_profit = max(max_profit, price - min_price)

        return max_profit
