from typing import List


class Solution:
    def max_array_sum(self, nums: List[int]) -> int:
        # 初始化当前最大子数组之和 全局最大子数组之和
        curr_max = nums[0]
        global_max = nums[0]

        for i in range(1, len(nums)):
            curr_max = max(nums[i], curr_max + nums[i])  # 扩展子数组还是从当前元素重新开始
            global_max = max(global_max, curr_max)  # 更新全局最大值

        return global_max


if __name__ == '__main__':
    nums = [-2, 1, -3, 4, -1, 2, 1, -5, 4]
    solution = Solution()
    print(solution.max_array_sum(nums))
