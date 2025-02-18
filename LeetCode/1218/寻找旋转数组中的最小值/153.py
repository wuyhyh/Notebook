def findMin(nums):
    left, right = 0, len(nums) - 1

    while left < right:
        mid = left + (right - left) // 2
        if nums[mid] > nums[right]:
            # 最小元素在 mid + 1 到 right 之间
            left = mid + 1
        else:
            # 最小元素在 left 到 mid 之间
            right = mid
    return nums[left]
