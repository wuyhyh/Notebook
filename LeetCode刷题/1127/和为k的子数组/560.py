def subarray_sum(nums, k):
    # 用于存储前缀和及其出现次数的字典
    prefix_sum_count = {0: 1}
    # 初始化当前的前缀和为 0
    current_sum = 0
    # 记录满足条件的子数组数量
    count = 0

    # 遍历数组中的每个元素
    for num in nums:
        # 更新当前的前缀和
        current_sum += num
        # 如果 (current_sum - k) 在字典中，说明存在一个子数组和为 k
        if current_sum - k in prefix_sum_count:
            count += prefix_sum_count[current_sum - k]
        # 更新前缀和在字典中的次数
        prefix_sum_count[current_sum] = prefix_sum_count.get(current_sum, 0) + 1

    return count

# 示例用法
nums = [1, 1, 1]
k = 2
print(subarray_sum(nums, k))  # 输出: 2
