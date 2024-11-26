def three_sum(nums):
    res = []
    nums.sort()  # 先对数组进行排序，方便后续使用双指针查找三元组
    n = len(nums)

    # 遍历数组中的每个元素，作为三元组中的第一个元素
    for i in range(n - 2):
        # 跳过重复元素，避免结果中出现重复的三元组
        if i > 0 and nums[i] == nums[i - 1]:
            continue

        # 初始化双指针，left 指向当前元素的下一个位置，right 指向数组末尾
        left, right = i + 1, n - 1
        while left < right:
            # 计算三元组的和
            total = nums[i] + nums[left] + nums[right]
            if total == 0:
                # 如果和为 0，找到一个符合条件的三元组，添加到结果中
                res.append([nums[i], nums[left], nums[right]])
                # 跳过重复的左指针元素，避免重复三元组
                while left < right and nums[left] == nums[left + 1]:
                    left += 1
                # 跳过重复的右指针元素，避免重复三元组
                while left < right and nums[right] == nums[right - 1]:
                    right -= 1
                # 移动指针，寻找新的组合
                left += 1
                right -= 1
            elif total < 0:
                # 如果和小于 0，说明需要更大的值，将左指针右移
                left += 1
            else:
                # 如果和大于 0，说明需要更小的值，将右指针左移
                right -= 1

    return res

# 示例用法
nums = [-1, 0, 1, 2, -1, -4]
print(three_sum(nums))  # 输出: [[-1, -1, 2], [-1, 0, 1]]
