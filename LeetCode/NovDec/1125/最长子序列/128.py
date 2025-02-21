def longest_consecutive(nums):
    # 如果输入列表为空，则返回 0，因为没有连续序列
    if not nums:
        return 0

    # 将列表转换为集合，以便进行 O(1) 时间复杂度的查找
    num_set = set(nums)
    longest_streak = 0

    # 遍历集合中的每个数字
    for num in num_set:
        # 只有当 'num' 是序列的开始时才进行计数
        # 这样可以确保每个序列只被统计一次
        if num - 1 not in num_set:
            current_num = num
            current_streak = 1

            # 通过递增 'current_num' 来计算当前序列的长度
            # 直到找不到更多的连续数字
            while current_num + 1 in num_set:
                current_num += 1
                current_streak += 1

            # 更新目前找到的最长序列长度
            longest_streak = max(longest_streak, current_streak)

    # 返回最长连续序列的长度
    return longest_streak

# 示例用法
nums = [100, 4, 200, 1, 3, 2]
print(longest_consecutive(nums))  # 输出: 4
