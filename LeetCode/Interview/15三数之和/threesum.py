from typing import List


class Solution:
    def threeSum(self, nums: List[int]) -> List[List[int]]:
        res = []
        nums.sort()  # 先排序，便于双指针查找
        n = len(nums)

        for i in range(n):
            if nums[i] > 0:  # 如果当前数字大于0，和一定大于0，不可能存在满足条件的组合
                break

            # 避免重复
            if i > 0 and nums[i] == nums[i - 1]:
                continue

            left, right = i + 1, n - 1
            while left < right:
                total = nums[i] + nums[left] + nums[right]
                if total == 0:
                    res.append([nums[i], nums[left], nums[right]])
                    # 跳过相同元素
                    while left < right and nums[left] == nums[left + 1]:
                        left += 1
                    while left < right and nums[right] == nums[right - 1]:
                        right -= 1
                    # 移动指针寻找下一个可能的解
                    left += 1
                    right -= 1
                elif total < 0:  # 增大和
                    left += 1
                else:
                    right -= 1  # 减小和

        return res


if __name__ == '__main__':
    sol = Solution()
    print(sol.threeSum([-1, 0, 1, 2, -1, -4]))
