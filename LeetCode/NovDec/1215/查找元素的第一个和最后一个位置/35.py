class Solution:
    def searchRange(self, nums: list[int], target: int) -> list[int]:
        # 查找第一个位置的二分查找
        def find_first():
            left, right = 0, len(nums) - 1
            while left <= right:
                mid = (left + right) // 2
                if nums[mid] < target:
                    left = mid + 1
                elif nums[mid] > target:
                    right = mid - 1
                else:
                    if mid == 0 or nums[mid - 1] != target:
                        return mid
                    right = mid - 1
            return -1

        # 查找最后一个位置的二分查找
        def find_last():
            left, right = 0, len(nums) - 1
            while left <= right:
                mid = (left + right) // 2
                if nums[mid] < target:
                    left = mid + 1
                elif nums[mid] > target:
                    right = mid - 1
                else:
                    if mid == len(nums) - 1 or nums[mid + 1] != target:
                        return mid
                    left = mid + 1
            return -1

        # 查找第一个和最后一个位置
        first = find_first()
        if first == -1:
            return [-1, -1]
        last = find_last()
        return [first, last]
