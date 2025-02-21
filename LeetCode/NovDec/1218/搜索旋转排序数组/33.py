def search(nums, target):
    left, right = 0, len(nums) - 1

    while left <= right:
        mid = (left + right) // 2

        if nums[mid] == target:  # 找到目标
            return mid

        # 判断哪一部分是有序的
        if nums[left] <= nums[mid]:
            # 左边有序
            if nums[left] <= target < nums[mid]:
                right = mid - 1  # target在左边
            else:
                left = mid + 1  # target在右边
        else:
            # 右边有序
            if nums[mid] < target <= nums[right]:
                left = mid + 1  # target在右边
            else:
                right = mid - 1  # target在左边

    return -1  # 未找到目标
