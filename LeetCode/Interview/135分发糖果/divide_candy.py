from typing import List


class Solution:
    def candy(self, ratings: List[int]) -> int:
        n = len(ratings)
        if n == 0:
            return 0

        # 贪心算法加双向遍历
        # 初始化两个糖果分发结果数组，默认每人一个
        left2right = [1] * n
        right2left = [1] * n

        # 从左到右遍历
        for i in range(1, n):
            if ratings[i] > ratings[i - 1]:
                left2right[i] = left2right[i - 1] + 1

        # 从右到左遍历
        for i in range(n - 2, -1, -1):
            if ratings[i] > ratings[i + 1]:
                right2left[i] = right2left[i + 1] + 1

        # 每个位置的最终数量取两个数组对应位置的最大值
        total_candies = 0
        for i in range(n):
            total_candies += max(left2right[i], right2left[i])

        return total_candies


if __name__ == '__main__':
    solution = Solution()
    ratings = [1, 0, 2]
    print(solution.candy(ratings))
