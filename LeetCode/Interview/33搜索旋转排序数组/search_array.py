from typing import List


class Solution:
    def search(self, nums: List[int], target: int) -> int:
        left, right = 0, len(nums) - 1

        while left <= right:
            mid = (left + right) // 2
            # 找到目标
            if nums[mid] == target:
                return mid

            # 判断左半部分是否有序
            if nums[left] <= nums[mid]:
                if nums[left] <= target < nums[mid]:
                    right = mid - 1  # 目标在左半边
                else:
                    left = mid + 1
            else:
                if nums[mid] < target <= nums[right]:
                    left = mid + 1
                else:
                    right = mid - 1

        return -1


if __name__ == '__main__':
    sol = Solution()
    nums = [4, 5, 6, 7, 0, 1, 2]
    print(sol.search(nums, 0))
