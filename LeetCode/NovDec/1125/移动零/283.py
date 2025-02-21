def move_zeroes(nums):
    # 初始化指针，表示下一个非零元素要放置的位置
    non_zero_index = 0

    # 遍历整个数组
    for i in range(len(nums)):
        # 如果当前元素不为零，则将其移动到 non_zero_index 位置
        if nums[i] != 0:
            nums[non_zero_index] = nums[i]
            non_zero_index += 1

    # 将剩余的位置填上零
    for i in range(non_zero_index, len(nums)):
        nums[i] = 0

# 示例用法
nums = [0, 1, 0, 3, 12]
move_zeroes(nums)
print(nums)  # 输出: [1, 3, 12, 0, 0]
