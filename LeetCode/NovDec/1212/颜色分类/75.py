class Solution:
    def sortColors(self, nums):
        low, mid, high = 0, 0, len(nums) - 1

        while mid <= high:
            if nums[mid] == 0:
                # 交换 nums[mid] 和 nums[low]
                nums[low], nums[mid] = nums[mid], nums[low]
                low += 1
                mid += 1
            elif nums[mid] == 1:
                mid += 1
            else:
                # 交换 nums[mid] 和 nums[high]
                nums[high], nums[mid] = nums[mid], nums[high]
                high -= 1
