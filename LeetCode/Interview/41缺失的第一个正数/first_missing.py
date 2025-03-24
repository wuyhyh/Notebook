from typing import List


class Solution:
    def first_missing_positive(self, nums: List[int]) -> int:
        n = len(nums)

        # 原地交换，将x放在x-1的位置上。然后再遍历，如果x[i]!=i,那就找到了，特殊情况就是n+1
        for i in range(n):
            while 1 <= nums[i] <= n and nums[nums[i] - 1] != nums[i]:
                new_index = nums[i] - 1
                nums[i], nums[new_index] = nums[new_index], nums[i]  # 原地交换

        # 找出不符合规律的位置
        for i in range(n):
            if nums[i] != i + 1:
                return i + 1

        return n + 1


if __name__ == '__main__':
    sol = Solution()
    nums = [3, 4, -1, 1]
    print(sol.first_missing_positive(nums))
