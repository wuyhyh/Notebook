def maxSubArray(nums):
    # 初始化最大和为第一个元素
    max_sum = nums[0]
    # 初始化当前子数组和为第一个元素
    current_sum = nums[0]

    # 从第二个元素开始遍历
    for i in range(1, len(nums)):
        # 判断是扩展当前子数组还是从当前元素重新开始子数组
        current_sum = max(current_sum + nums[i], nums[i])

        # 更新最大子数组和
        max_sum = max(max_sum, current_sum)

    return max_sum
